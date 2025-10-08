#!/usr/bin/env python3
"""
Split updated Varanasi (1).json into individual category files with _id metadata.
Updates the existing Varanasi category files with new data.

Input: data/varanasi/Varanasi (1).json
Output: data/varanasi/Category_varanasi.json files (12 categories) - OVERWRITES existing files

Removes __v fields and preserves all other data including _id.
"""

import json
import os
from pathlib import Path

def split_updated_varanasi_data():
    # Paths
    base_dir = Path("data/varanasi")
    input_file = base_dir / "Varanasi (1).json"
    
    if not input_file.exists():
        print(f"❌ Error: {input_file} not found!")
        return
    
    # Load updated file
    print(f"📖 Loading updated {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Found {len(data)} categories in updated Varanasi (1).json")
    
    # Category mapping (lowercase from file → PascalCase for filenames)
    # Keep exactly the same as before
    category_mapping = {
        'accommodation': 'Accommodation',
        'activity': 'Activity', 
        'cityinfo': 'Cityinfo',  # Keep lowercase in key for consistency
        'connectivity': 'Connectivity',
        'food': 'Food',
        'hiddengem': 'Hiddengem',  # Keep lowercase in key for consistency
        'itinerary': 'Itinerary',
        'misc': 'Misc',
        'nearbyspot': 'Nearbyspot',  # Keep lowercase in key for consistency
        'place': 'Place',
        'shop': 'Shop',
        'transport': 'Transport',
    }
    
    total_processed = 0
    
    print(f"\\n🔄 Updating existing Varanasi category files...")
    
    for source_key, target_category in category_mapping.items():
        if source_key not in data:
            print(f"⚠️  Category '{source_key}' not found in updated Varanasi (1).json")
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
        
        # Create output file with lowercase key (same naming as before)
        output_file = base_dir / f"{target_category}_varanasi.json"
        output_data = {source_key: cleaned_items}  # Use original lowercase key
        
        # Write to file (overwrites existing)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {target_category:12} → {output_file.name:25} ({len(cleaned_items)} items, {items_with_id} with _id)")
        total_processed += len(cleaned_items)
    
    print(f"\\n🎉 Successfully updated Varanasi files with {total_processed} items!")
    print(f"📁 Files updated in: {base_dir}")
    
    # Show comparison
    print(f"\\n📊 Data comparison:")
    print(f"   Previous total: 185 items")
    print(f"   Updated total:  {total_processed} items")
    print(f"   Difference:     {total_processed - 185:+d} items")
    
    # Verify all files were updated
    updated_files = list(base_dir.glob("*_varanasi.json"))
    print(f"\\n📋 Updated files ({len(updated_files)}):")
    for file in sorted(updated_files):
        print(f"   • {file.name}")

if __name__ == "__main__":
    split_updated_varanasi_data()
