import requests
import sys
from database import init_db, add_verses

def ingest_dhammapada():
    init_db()
    print("Downloading the Dhammapada (F. Max Muller translation)...")
    print("Fetching 423 verses (this takes 2-5 minutes):\n")
    
    all_verses = []
    seen_refs = set()
    
    for verse_num in range(1, 424):
        url = f"https://api.urantia.dev/scriptures/dhammapada/{verse_num}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                passages = data.get("data", {}).get("passages", [])
                
                for p in passages:
                    ref = p["ref"]
                    if ref in seen_refs:
                        continue
                    seen_refs.add(ref)
                    
                    all_verses.append({
                        "faith": "Buddhism",
                        "scripture": "Dhammapada",
                        "source_id": f"dhammapada:{ref.replace(' ', '_')}",
                        "citation": ref,
                        "text": p["text"],
                        "translation_name": "F. Max Muller (1881)",
                        "language": "en",
                        "themes": ""
                    })
            
            # Print a dot every 10 verses so you can see progress
            if verse_num % 10 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
                
        except Exception as e:
            pass
            
    print(f"\n\nParsed {len(all_verses)} Dhammapada verses.")
    print("Inserting into database...")
    add_verses(all_verses)
    print("Dhammapada ingestion complete!")

if __name__ == "__main__":
    ingest_dhammapada()
