import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client
import json

load_dotenv()
from system_prompt import SYSTEM_PROMPT

app = FastAPI(title="ORACLE Backend", version="3.0.0")

print("Initializing AI and Cloud Database...")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
embedder = SentenceTransformer('all-MiniLM-L6-v2')
print("Cloud Database and AI ready.")

class AskRequest(BaseModel):
    question: str

def retrieve(question: str, k_per_faith: int = 2) -> list:
    # 1. Embed the user's question
    q_embedding = embedder.encode([question]).tolist()[0]
    
    verses = []
    # 2. Query Supabase separately for each tradition
    faiths = ["Islam", "Christianity", "Judaism", "Buddhism", "Hindu traditions"]
    
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
            print("\n=== GROQ API ERROR ===")
            print(str(e))
            print("========================\n")
            out = deterministic_answer(req.question, verses)
            out["llm_error"] = str(e)
            return out
            
    return deterministic_answer(req.question, verses)

@app.get("/")
def read_root():
    return FileResponse("static/index.html", media_type="text/html")
