#!/usr/bin/env python3
"""
Split updated Rishikesh (1).json into individual category files with _id metadata.
Updates the existing Rishikesh category files with new data.

NOTE: Rishikesh currently has PascalCase keys in existing files, 
but new data has lowercase keys. We'll update to maintain consistency with other cities.

Input: data/rishikesh/Rishikesh (1).json
Output: data/rishikesh/Category_rishikesh.json files (12 categories) - OVERWRITES existing files

Removes __v fields and preserves all other data including _id.
"""

import json
import os
from pathlib import Path

def split_updated_rishikesh_data():
    # Paths
    base_dir = Path("data/rishikesh")
    input_file = base_dir / "Rishikesh (1).json"
    
    if not input_file.exists():
        print(f"❌ Error: {input_file} not found!")
        return
    
    # Load updated file
    print(f"📖 Loading updated {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Found {len(data)} categories in updated Rishikesh (1).json")
    
    # Category mapping (lowercase from file → PascalCase for filenames)
    # Keep consistent with other cities (lowercase keys in files)
    category_mapping = {
        'accommodation': 'Accommodation',
        'activity': 'Activity', 
        'cityinfo': 'CityInfo',  # Note: Rishikesh currently uses PascalCase, will update for consistency
        'connectivity': 'Connectivity',
        'food': 'Food',
        'hiddengem': 'HiddenGem',  # Note: Rishikesh currently uses PascalCase, will update for consistency
        'itinerary': 'Itinerary',
        'misc': 'Misc',
        'nearbyspot': 'NearbySpot',  # Note: Rishikesh currently uses PascalCase, will update for consistency
        'place': 'Place',
        'shop': 'Shop',
        'transport': 'Transport',
    }
    
    total_processed = 0
    
    print(f"\\n🔄 Updating existing Rishikesh category files...")
    print(f"⚠️  Note: Converting Rishikesh to lowercase keys for consistency with other cities")
    
    for source_key, target_category in category_mapping.items():
        if source_key not in data:
            print(f"⚠️  Category '{source_key}' not found in updated Rishikesh (1).json")
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
        
        # Create output file with lowercase key (consistent with other cities)
        output_file = base_dir / f"{target_category}_rishikesh.json"
        output_data = {source_key: cleaned_items}  # Use lowercase key for consistency
        
        # Write to file (overwrites existing)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {target_category:12} → {output_file.name:30} ({len(cleaned_items)} items, {items_with_id} with _id)")
        total_processed += len(cleaned_items)
    
    print(f"\\n🎉 Successfully updated Rishikesh files with {total_processed} items!")
    print(f"📁 Files updated in: {base_dir}")
    
    # Show comparison
    print(f"\\n📊 Data comparison:")
    print(f"   Previous total: 190 items")
    print(f"   Updated total:  {total_processed} items")
    print(f"   Difference:     {total_processed - 190:+d} items")
    
    print(f"\\n⚠️  Important: Rishikesh indexing script needs to be updated to use lowercase keys!")
    
    # Verify all files were updated
    updated_files = list(base_dir.glob("*_rishikesh.json"))
    print(f"\\n📋 Updated files ({len(updated_files)}):")
    for file in sorted(updated_files):
        print(f"   • {file.name}")

if __name__ == "__main__":
    split_updated_rishikesh_data()
