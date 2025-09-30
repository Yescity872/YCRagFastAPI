#!/usr/bin/env python3
"""
Split Varanasi.json into 12 separate category files.
Removes "__v" field from all items as requested.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

def remove_version_field(item: Dict[str, Any]) -> Dict[str, Any]:
    """Remove __v field from item"""
    clean_item = dict(item)
    clean_item.pop('__v', None)
    return clean_item

def create_category_file(category: str, items: List[Dict[str, Any]], output_dir: Path):
    """Create individual category file"""
    if not items:
        print(f"⚠️  {category}: No items found, creating empty file")
        items = []
    
    # Clean items by removing __v field
    clean_items = [remove_version_field(item) for item in items]
    
    # Create file structure
    file_data = {category.title(): clean_items}
    
    # Write to file
    filename = f"{category.title()}_varanasi.json"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(file_data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Created {filename}: {len(clean_items)} items")

def main():
    # Paths
    base_dir = Path("/Users/kartik/Documents/YCRagFastAPI/data/varanasi")
    input_file = base_dir / "Varanasi.json"
    
    # Load main file
    print("📂 Loading Varanasi.json...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 12 categories to extract
    categories = [
        "accommodation", "activity", "cityinfo", "connectivity", 
        "food", "hiddengem", "itinerary", "misc", 
        "nearbyspot", "place", "shop", "transport"
    ]
    
    print("🔄 Creating category files...\n")
    
    total_items = 0
    for category in categories:
        items = data.get(category, [])
        create_category_file(category, items, base_dir)
        total_items += len(items)
    
    print(f"\n✨ Split complete!")
    print(f"📊 Total items processed: {total_items}")
    print(f"📁 Files created in: {base_dir}")

if __name__ == "__main__":
    main()
