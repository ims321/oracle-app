import sqlite3
from database import init_db, add_verses

def clear_db():
    conn = sqlite3.connect('oracle.db')
    conn.execute('DELETE FROM verses')
    conn.commit()
    conn.close()
    print("Cleared old data.")

# A curated dataset of 40 verses across 4 traditions
real_data = [
    # --- JUDAISM ---
    {"faith": "Judaism", "citation": "Genesis 1:1", "text": "In the beginning God created the heaven and the earth.", "themes": "creation,god"},
    {"faith": "Judaism", "citation": "Deuteronomy 15:11", "text": "There will never cease to be needy ones in your land—therefore I command you: open your hand to the poor and needy.", "themes": "charity,poverty"},
    {"faith": "Judaism", "citation": "Leviticus 19:18", "text": "Do not take vengeance or bear a grudge against your kin; love your neighbor as yourself.", "themes": "love,neighbor"},
    {"faith": "Judaism", "citation": "Exodus 20:13", "text": "You shall not murder.", "themes": "murder,law"},
    {"faith": "Judaism", "citation": "Micah 6:8", "text": "What does the Lord require of you? To act justly and to love mercy and to walk humbly with your God.", "themes": "justice,mercy"},
    {"faith": "Judaism", "citation": "Psalm 23:1", "text": "The Lord is my shepherd; I shall not want.", "themes": "trust,comfort"},
    {"faith": "Judaism", "citation": "Proverbs 3:5", "text": "Trust in the Lord with all your heart and lean not on your own understanding.", "themes": "trust,wisdom"},
    {"faith": "Judaism", "citation": "Isaiah 2:4", "text": "They shall beat their swords into plowshares, and their spears into pruning hooks; nation shall not lift up sword against nation.", "themes": "peace,war"},
    {"faith": "Judaism", "citation": "Ecclesiastes 3:1", "text": "To every thing there is a season, and a time to every purpose under the heaven.", "themes": "time,purpose"},
    {"faith": "Judaism", "citation": "Deuteronomy 6:5", "text": "Love the Lord your God with all your heart and with all your soul and with all your strength.", "themes": "love,god"},

    # --- CHRISTIANITY ---
    {"faith": "Christianity", "citation": "John 3:16", "text": "For God so loved the world that he gave his only Son, so that everyone who believes in him may not perish but may have eternal life.", "themes": "love,salvation"},
    {"faith": "Christianity", "citation": "Acts 2:44-45", "text": "All who believed were together and had all things in common; they would sell their possessions and distribute to all, as any had need.", "themes": "charity,community"},
    {"faith": "Christianity", "citation": "Matthew 5:38-39", "text": "You have heard that it was said, 'An eye for an eye and a tooth for a tooth.' But I say to you, do not resist an evildoer. If anyone strikes you on the right cheek, turn the other also.", "themes": "forgiveness,retaliation"},
    {"faith": "Christianity", "citation": "Matthew 22:37-39", "text": "You shall love the Lord your God with all your heart, and with all your soul, and with all your mind. This is the greatest and first commandment. And a second is like it: You shall love your neighbor as yourself.", "themes": "love,commandment"},
    {"faith": "Christianity", "citation": "1 Corinthians 13:4", "text": "Love is patient; love is kind; love is not envious or boastful or arrogant or rude.", "themes": "love,character"},
    {"faith": "Christianity", "citation": "Romans 12:19", "text": "Beloved, never avenge yourselves, but leave room for the wrath of God; for it is written, 'Vengeance is mine, I will repay, says the Lord.'", "themes": "vengeance,justice"},
    {"faith": "Christianity", "citation": "Matthew 5:9", "text": "Blessed are the peacemakers, for they will be called children of God.", "themes": "peace,blessing"},
    {"faith": "Christianity", "citation": "Genesis 1:27", "text": "So God created humankind in his image, in the image of God he created them; male and female he created them.", "themes": "creation,humanity"},
    {"faith": "Christianity", "citation": "Philippians 4:13", "text": "I can do all things through him who strengthens me.", "themes": "strength,faith"},
    {"faith": "Christianity", "citation": "Matthew 6:24", "text": "No one can serve two masters; for a slave will either hate the one and love the other, or be devoted to the one and despise the other. You cannot serve God and wealth.", "themes": "wealth,devotion"},

    # --- ISLAM ---
    {"faith": "Islam", "citation": "Quran 9:60", "text": "Zakat expenditures are only for the poor and the needy, and those employed to collect it, and for those whose hearts are to be reconciled, and for the freeing of slaves, and for those in debt, and for the cause of Allah, and for the traveler.", "themes": "charity,zakat"},
    {"faith": "Islam", "citation": "Quran 42:40", "text": "The retribution for an evil act is an evil one like it, but whoever pardons and makes reconciliation—his reward is with Allah.", "themes": "forgiveness,retaliation"},
    {"faith": "Islam", "citation": "Quran 2:190-193", "text": "Fight in the way of Allah those who fight you, but do not transgress. Indeed, Allah does not like transgressors. If they cease, then there is to be no aggression except against the oppressors.", "themes": "war,peace"},
    {"faith": "Islam", "citation": "Quran 5:32", "text": "Whoever kills a soul unless for a soul or for corruption in the land—it is as if he had slain mankind entirely. And whoever saves one—it is as if he had saved mankind entirely.", "themes": "murder,sanctity"},
    {"faith": "Islam", "citation": "Quran 17:23", "text": "Your Lord has decreed that you worship none but Him, and that you be kind to parents. Whether one or both of them attain old age in your life, say not to them a word of contempt, nor repel them, but address them in terms of honor.", "themes": "parents,respect"},
    {"faith": "Islam", "citation": "Quran 49:13", "text": "O mankind, indeed We have created you from male and female and made you peoples and tribes that you may know one another. Indeed, the most noble of you in the sight of Allah is the most righteous of you.", "themes": "diversity,righteousness"},
    {"faith": "Islam", "citation": "Quran 2:177", "text": "Righteousness is not that you turn your faces toward the east or the west, but [true] righteousness is [in] one who believes in Allah, the Last Day, the angels, the Book, and the prophets and gives wealth, in spite of love for it, to relatives, orphans, the needy, the traveler, those who ask, and for freeing slaves.", "themes": "charity,righteousness"},
    {"faith": "Islam", "citation": "Quran 2:256", "text": "There shall be no compulsion in [acceptance of] the religion. The right course has become clear from the wrong.", "themes": "freedom,religion"},
    {"faith": "Islam", "citation": "Quran 3:134", "text": "Who spend [in the cause of Allah] during ease and hardship and who restrain anger and who pardon the people - and Allah loves the doers of good.", "themes": "charity,forgiveness"},
    {"faith": "Islam", "citation": "Quran 14:7", "text": "And [remember] when your Lord proclaimed, 'If you are grateful, I will surely increase you [in favor]; but if you deny, indeed, My punishment is severe.'", "themes": "gratitude,blessing"},

    # --- HINDUISM ---
    {"faith": "Hindu traditions", "citation": "Bhagavad Gita 17:20", "text": "Giving is sattvic when it is given to one who cannot return it, at the right place and time, to a worthy person.", "themes": "charity,dana"},
    {"faith": "Hindu traditions", "citation": "Bhagavad Gita 2:47", "text": "You have a right to your actions, but never to the fruits of your actions. Let not the fruits of action be your motive, nor let your attachment be to inaction.", "themes": "action,karma"},
    {"faith": "Hindu traditions", "citation": "Bhagavad Gita 1:31-2:3", "text": "Arjuna is distressed at the prospect of killing kin; Krishna calls him to act without attachment to the fruits of action.", "themes": "war,duty"},
    {"faith": "Hindu traditions", "citation": "Manusmriti 8:14", "text": "Punishment governs the world; it is the foundation of order and the guardian of the law.", "themes": "punishment,justice"},
    {"faith": "Hindu traditions", "citation": "Rig Veda 10:191", "text": "Assemble together, speak with one voice, let your minds be of one accord, even as the gods of old sit together in harmony.", "themes": "unity,harmony"},
    {"faith": "Hindu traditions", "citation": "Mahabharata 12:251", "text": "Non-violence is the highest duty. It is truth, it is forgiveness, it is peace.", "themes": "ahimsa,peace"},
    {"faith": "Hindu traditions", "citation": "Upanishads (Brihadaranyaka 1.3.28)", "text": "Lead me from the unreal to the real. Lead me from darkness to light. Lead me from death to immortality.", "themes": "truth,light"},
    {"faith": "Hindu traditions", "citation": "Bhagavad Gita 12:13-14", "text": "One who is not envious but is a kind friend to all living entities, who does not think himself a proprietor and is free from false ego, who is equal in both happiness and distress, who is tolerant, always satisfied, self-controlled, and engaged in devotional service with determination, his mind and intelligence fixed on Me—such a devotee of Mine is very dear to Me.", "themes": "compassion,devotion"},
    {"faith": "Hindu traditions", "citation": "Taittiriya Upanishad 1.11.1", "text": "Speak the truth. Practice virtue. Do not neglect the study of the Vedas. Having brought a gift to your teacher, do not cut off the line of descendants.", "themes": "truth,virtue"},
    {"faith": "Hindu traditions", "citation": "Bhagavad Gita 6:5", "text": "One must elevate oneself by one's own mind, and not degrade oneself. The mind is the friend of the conditioned soul, and its enemy as well.", "themes": "self,mind"}
]

if __name__ == "__main__":
    init_db()
    clear_db()
    add_verses(real_data)
    print(f"Successfully ingested {len(real_data)} high-quality, real verses into the database.")
