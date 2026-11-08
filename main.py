import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from supabase import create_client
from fastembed import TextEmbedding
import json

load_dotenv()
from system_prompt import SYSTEM_PROMPT

app = FastAPI(title="ORACLE Backend", version="5.0.0")

print("Initializing Cloud Database and FastEmbed...")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
embedder = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
print("Database and FastEmbed ready.")

class AskRequest(BaseModel):
    question: str
    faiths: List[str]

class LearnRequest(BaseModel):
    faith: str

def get_embedding(text: str) -> list:
    embeddings = list(embedder.embed([text]))
    return embeddings[0].tolist()

def retrieve(question: str, selected_faiths: List[str], k_per_faith: int = 2) -> list:
    q_embedding = get_embedding(question)
    if not q_embedding:
        return []
        
    verses = []
    for faith in selected_faiths:
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
    return json.loads(resp.choices[0].message.content)

@app.post("/api/ask")
def ask(req: AskRequest):
    verses = retrieve(req.question, req.faiths)
    if not verses:
        return {"universal_thread": None, "aligned_verses": [], "distinct_rationales": [], "insufficient_evidence": "No relevant passages found."}
    
    try:
        return llm_answer(req.question, verses)
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/learn")
def learn(req: LearnRequest):
    from openai import OpenAI
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    prompt = f"""You are an expert professor of comparative religion. Create a 5-step learning curriculum for a student who wants to understand {req.faith}.
    Return strict JSON with this structure:
    {{
        "tradition": "{req.faith}",
        "description": "A 2-sentence overview of what this tradition is.",
        "curriculum": [
            {{"step": 1, "title": "Title of step 1", "summary": "1 sentence summary of what will be taught."}},
            {{"step": 2, "title": "Title of step 2", "summary": "1 sentence summary of what will be taught."}},
            {{"step": 3, "title": "Title of step 3", "summary": "1 sentence summary of what will be taught."}},
            {{"step": 4, "title": "Title of step 4", "summary": "1 sentence summary of what will be taught."}},
            {{"step": 5, "title": "Title of step 5", "summary": "1 sentence summary of what will be taught."}}
        ]
    }}
    """
    
    resp = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(resp.choices[0].message.content)

@app.get("/")
def read_root():
    return FileResponse("static/index.html", media_type="text/html")
