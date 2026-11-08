import os
import chromadb
from supabase import create_client
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("ERROR: SUPABASE_URL or SUPABASE_KEY is missing in .env")
    exit(1)

supabase = create_client(url, key)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="scriptures")

# Get total count first
total = collection.count()
print(f"Found {total} verses in ChromaDB. Migrating to Supabase...")

batch_size = 200
success_count = 0

for offset in tqdm(range(0, total, batch_size)):
    # Fetch a chunk from ChromaDB using limit and offset
    data = collection.get(
        limit=batch_size,
        offset=offset,
        include=["metadatas", "documents", "embeddings"]
    )
    
    if not data['ids']:
        break
        
    rows = []
    for j in range(len(data['ids'])):
        # Supabase pgvector expects the embedding as a string like "[0.1, 0.2, ...]"
        embedding_str = f"[{','.join(map(str, data['embeddings'][j]))}]"
        meta = data['metadatas'][j]
        
        rows.append({
            "faith": meta["faith"],
            "scripture": meta["scripture"],
            "source_id": meta["source_id"],
            "citation": meta["citation"],
            "text": data['documents'][j],
            "embedding": embedding_str
        })
        
    try:
        supabase.table("scriptures").insert(rows).execute()
        success_count += len(rows)
    except Exception as e:
        print(f"\nERROR inserting batch starting at {offset}: {e}")

print(f"\nMigration complete! Successfully inserted {success_count} verses.")
