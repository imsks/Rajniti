"""
Initialize politician_metadata.json with all politician IDs and current timestamp.
Run this script once to populate metadata.
"""
import json
from pathlib import Path
from datetime import datetime

def init_metadata():
    """Initialize metadata with all politicians from mla.json and mp.json."""
    data_dir = Path(__file__).resolve().parent.parent / "app" / "data"
    metadata_path = data_dir / "politician_metadata.json"
    
    metadata = {
        "updated_at_map": {},
        "last_batch_update": datetime.utcnow().isoformat() + "Z"
    }
    
    now = datetime.utcnow().isoformat() + "Z"
    
    # Load and process MLA data
    mla_path = data_dir / "mla.json"
    if mla_path.exists():
        with open(mla_path, "r", encoding="utf-8") as f:
            mla_data = json.load(f)
        
        for politician in mla_data:
            pid = str(politician.get("id", ""))
            if pid:
                metadata["updated_at_map"][pid] = now
        
        print(f"✅ Added {len(mla_data)} MLA politicians to metadata")
    
    # Load and process MP data
    mp_path = data_dir / "mp.json"
    if mp_path.exists():
        with open(mp_path, "r", encoding="utf-8") as f:
            mp_data = json.load(f)
        
        for politician in mp_data:
            pid = str(politician.get("id", ""))
            if pid:
                metadata["updated_at_map"][pid] = now
        
        print(f"✅ Added {len(mp_data)} MP politicians to metadata")
    
    # Write metadata
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        f.write("\n")
    
    print(f"✅ Metadata initialized with {len(metadata['updated_at_map'])} politicians")
    print(f"📝 File: {metadata_path}")

if __name__ == "__main__":
    init_metadata()
