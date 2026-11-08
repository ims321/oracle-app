import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client
from fastembed import TextEmbedding
import json

load_dotenv()
from system_prompt import SYSTEM_PROMPT

app = FastAPI(title="ORACLE Backend", version="3.4.0")

print("Initializing Cloud Database and FastEmbed...")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
embedder = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
print("Database and FastEmbed ready.")

class AskRequest(BaseModel):
    question: str

def get_embedding(text: str) -> list:
    embeddings = list(embedder.embed([text]))
    return embeddings[0].tolist()

def retrieve(question: str, k_per_faith: int = 2) -> list:
    q_embedding = get_embedding(question)
    if not q_embedding:
        return []
        
    verses = []
    # Updated list of all 10 traditions
    faiths = [
        "Islam", "Christianity", "Judaism", "Buddhism", 
        "Hindu traditions", "Stoicism", "Taoism", 
        "Sikhism", "Confucianism", "Contemporary Teachers"
    ]
    
    for faith in faiths:
        try:
            res = supabase.rpc('match_scriptures', {
                'query_embedding': q_embedding,
                'match_threshold': 0.0,
                'match_count': k_per_faith,
                'p_faith': faith
            }).execute()
            
            if res.data:
                for item in res.data:
                    verses.append({
                        "faith": item["faith"],
                        "citation": item["citation"],
                        "text": item["text"]
                    })
        except Exception as e:
            print(f"Error retrieving for {faith}: {e}")
            
    return verses

def deterministic_answer(question: str, verses: list) -> dict:
    if not verses:
        return {"universal_thread": None, "aligned_verses": [], "distinct_rationales": [], "disagreements": [], "insufficient_evidence": "No relevant passages found.", "mode": "deterministic"}
    faiths = list(set(v["faith"] for v in verses))
    return {
        "universal_thread": f"Retrieved passages from {', '.join(faiths)} touch this question.",
        "aligned_verses": verses,
        "distinct_rationales": [{"faith": f, "theological_logic": "Rationale requires an API key."} for f in faiths],
        "disagreements": [{"issue": "Interpretation", "positions": "Not evaluated."}],
        "insufficient_evidence": None,
        "mode": "deterministic",
    }

def llm_answer(question: str, verses: list) -> dict:
    from openai import OpenAI
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY")
    )
    context = "\n".join(f"[{v['faith']} | {v['citation']}] {v['text']}" for v in verses)
    
    resp = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {question}\n\nRetrieved sources:\n{context}"},
        ],
    )
    data = json.loads(resp.choices[0].message.content)
    data["mode"] = "llm"
    return data

@app.post("/api/ask")
def ask(req: AskRequest):
    verses = retrieve(req.question)
    
    if os.getenv("GROQ_API_KEY"):
        try:
            return llm_answer(req.question, verses)
        except Exception as e:
            print(f"Groq Error: {e}")
            out = deterministic_answer(req.question, verses)
            out["llm_error"] = str(e)
            return out
            
    return deterministic_answer(req.question, verses)

@app.get("/")
def read_root():
    return FileResponse("static/index.html", media_type="text/html")
