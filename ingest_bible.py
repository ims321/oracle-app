import json
import urllib.request
from database import init_db, add_verses

def ingest_bible():
    init_db()
    print("Downloading the complete Bible (KJV)...")
    url = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/en_kjv.json"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Failed to download Bible: {e}")
        return

    all_verses = []
    for book in data:
        book_name = book['name']
        # Separate Old Testament (Judaism) from New Testament (Christianity)
        faith = "Judaism" if book.get('testament') == 'old' else "Christianity"
        
        for chapter_idx, chapter in enumerate(book['chapters']):
            for verse_idx, text in enumerate(chapter):
                all_verses.append({
                    "faith": faith,
                    "scripture": book_name,
                    "source_id": f"bible:{book_name}:{chapter_idx+1}:{verse_idx+1}",
                    "citation": f"{book_name} {chapter_idx+1}:{verse_idx+1}",
                    "text": text,
                    "translation_name": "King James Version",
                    "language": "en",
                    "themes": ""
                })
                
    print(f"Parsed {len(all_verses)} Bible verses.")
    print("Inserting into database...")
    add_verses(all_verses)
    print("Bible ingestion complete!")

if __name__ == "__main__":
    ingest_bible()
