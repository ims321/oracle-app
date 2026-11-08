import sqlite3
from database import init_db, add_verses

# 1. Initialize fresh database
init_db()

# 2. The correct verses for "wealth and charity"
real_data = [
    {
        "faith": "Judaism",
        "citation": "Deuteronomy 15:11",
        "text": "There will never cease to be needy ones in your land—therefore I command you: open your hand to the poor and needy.",
        "themes": "charity,wealth,poverty"
    },
    {
        "faith": "Christianity",
        "citation": "Acts 2:44-45",
        "text": "All who believed were together and had all things in common; they would sell their possessions and distribute to all, as any had need.",
        "themes": "charity,wealth,community"
    },
    {
        "faith": "Islam",
        "citation": "Quran 9:60",
        "text": "Zakat expenditures are only for the poor and the needy, and those employed to collect it.",
        "themes": "charity,zakat,wealth"
    },
    {
        "faith": "Hindu traditions",
        "citation": "Bhagavad Gita 17:20",
        "text": "Giving is sattvic when it is given to one who cannot return it, at the right place and time, to a worthy person.",
        "themes": "charity,dana,wealth"
    }
]

# 3. Insert data
add_verses(real_data)
print(f"Successfully reset database and ingested {len(real_data)} correct verses.")
