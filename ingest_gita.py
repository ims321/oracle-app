import json
import urllib.request
from database import init_db, add_verses

def ingest_gita():
    init_db()
    print("Downloading the Bhagavad Gita (Sanskrit + English)...")
    
    base_url = "https://raw.githubusercontent.com/praneshp1org/Bhagavad-Gita-JSON-data/main/"
    
    # 1. Download the verses
    try:
        req = urllib.request.Request(base_url + "verse.json", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            verses_data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Failed to download verses: {e}")
        return

    # 2. Download the translations (using utf-8-sig to handle the BOM)
    try:
        req = urllib.request.Request(base_url + "translation.json", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            translations_data = json.loads(response.read().decode('utf-8-sig'))
    except Exception as e:
        print(f"Failed to download translations: {e}")
        return

    # 3. Build a lookup dictionary for translations
    # We only want English translations. We'll use Swami Sivananda (author_id 16)
    translation_lookup = {}
    for t in translations_data:
        if t["lang"] == "english" and t["author_id"] == 16:
            translation_lookup[t["verse_id"]] = t["description"]

    # 4. Combine the data
    all_verses = []
    for v in verses_data:
        verse_id = v["id"]
        english_text = translation_lookup.get(verse_id)
        
        if english_text:
            chapter = v["chapter_number"]
            verse_num = v["verse_number"]
            
            all_verses.append({
                "faith": "Hindu traditions",
                "scripture": "Bhagavad Gita",
                "source_id": f"gita:{chapter}:{verse_num}",
                "citation": f"Bhagavad Gita {chapter}:{verse_num}",
                "text": english_text,
                "translation_name": "Swami Sivananda",
                "language": "en",
                "themes": ""
            })

    print(f"Parsed {len(all_verses)} Gita verses with English translations.")
    print("Inserting into database...")
    add_verses(all_verses)
    print("Bhagavad Gita ingestion complete!")

if __name__ == "__main__":
    ingest_gita()
