import chromadb
from database import get_all_verses
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

def migrate():
    print("Loading verses from SQLite...")
    verses = get_all_verses()
    print(f"Found {len(verses)} verses. Starting migration to ChromaDB...")

    # Initialize ChromaDB (saves to a local folder called 'chroma_db')
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Delete the collection if it exists so we start fresh
    try:
        client.delete_collection(name="scriptures")
    except:
        pass
        
    collection = client.create_collection(name="scriptures")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')

    # Process in batches to avoid overwhelming the Mac's memory
    batch_size = 1000
    for i in tqdm(range(0, len(verses), batch_size)):
        batch = verses[i:i+batch_size]
        
        documents = [v["text"] for v in batch]
        metadatas = [{
            "faith": v["faith"], 
            "scripture": v["scripture"], 
            "citation": v["citation"], 
            "source_id": v["source_id"]
        } for v in batch]
        ids = [v["source_id"] for v in batch]
        
        # Create embeddings and add to ChromaDB
        embeddings = embedder.encode(documents).tolist()
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    print("\nMigration complete! Your vector database is ready.")

if __name__ == "__main__":
    migrate()
