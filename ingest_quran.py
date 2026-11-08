import json
import urllib.request
from database import init_db, add_verses

def ingest_quran():
    init_db()
    print("Downloading the complete Quran (Saheeh International translation)...")
    
    # This single JSON file contains the entire Quran
    url = "https://cdn.jsdelivr.net/npm/quran-cloud@1.0.0/dist/quran_en.json"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Failed to download Quran data: {e}")
        return

    all_verses = []
    
    # The JSON is an array of chapters (surahs)
    for chapter in data:
        surah_num = chapter["id"]
        for verse in chapter["verses"]:
            ayah_num = verse["id"]
            all_verses.append({
                "faith": "Islam",
                "scripture": "Quran",
                "source_id": f"quran:{surah_num}:{ayah_num}",
                "citation": f"Quran {surah_num}:{ayah_num}",
                "text": verse["translation"],
                "translation_name": "Saheeh International",
                "language": "en",
                "themes": ""
            })
            
    print(f"Parsed {len(all_verses)} verses from the Quran.")
    print("Inserting into database...")
    add_verses(all_verses)
    print("Quran ingestion complete!")

if __name__ == "__main__":
    ingest_quran()
