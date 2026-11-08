import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "oracle.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # CREATE TABLE IF NOT EXISTS prevents deleting old data
    c.execute('''CREATE TABLE IF NOT EXISTS verses (
                 id INTEGER PRIMARY KEY,
                 faith TEXT,
                 scripture TEXT,
                 source_id TEXT UNIQUE,
                 citation TEXT,
                 text TEXT,
                 translation_name TEXT,
                 language TEXT,
                 themes TEXT)''')
    conn.commit()
    conn.close()

def add_verses(verses_list):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for v in verses_list:
        try:
            c.execute("""INSERT OR IGNORE INTO verses 
                         (faith, scripture, source_id, citation, text, translation_name, language, themes) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                      (v.get("faith"), v.get("scripture"), v.get("source_id"), 
                       v.get("citation"), v.get("text"), v.get("translation_name"), 
                       v.get("language"), v.get("themes", "")))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

def get_all_verses():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT faith, scripture, citation, text, source_id FROM verses")
    rows = c.fetchall()
    conn.close()
    return [{"faith": r[0], "scripture": r[1], "citation": r[2], "text": r[3], "source_id": r[4]} for r in rows]
