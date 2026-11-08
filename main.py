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

app = FastAPI(title="ORACLE Backend", version="6.1.0")

print("Initializing Cloud Database and FastEmbed...")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
embedder = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

class AskRequest(BaseModel):
    question: str
    faiths: List[str]

class LearnRequest(BaseModel):
    faith: str

class InterfaithRequest(BaseModel):
    faith_a: str
    faith_b: str
    topic: str

def get_embedding(text: str) -> list:
    embeddings = list(embedder.embed([text]))
    return embeddings[0].tolist()

def retrieve(question: str, selected_faiths: List[str], k_per_faith: int = 2) -> list:
    q_embedding = get_embedding(question)
    verses = []
    for faith in selected_faiths:
        try:
            res = supabase.rpc('match_scriptures', {
                'query_embedding': q_embedding, 'match_threshold': 0.0, 'match_count': k_per_faith, 'p_faith': faith
            }).execute()
            if res.data:
                for item in res.data:
                    verses.append({"faith": item["faith"], "citation": item["citation"], "text": item["text"]})
        except Exception:
            pass
    return verses

@app.post("/api/ask")
def ask(req: AskRequest):
    verses = retrieve(req.question, req.faiths)
    if not verses:
        return {"universal_thread": "No relevant passages found.", "aligned_verses": [], "distinct_rationales": [], "insufficient_evidence": "True"}
    
    from openai import OpenAI
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))
    context = "\n".join(f"[{v['faith']} | {v['citation']}] {v['text']}" for v in verses)
    
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b", temperature=0.2, response_format={"type": "json_object"},
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Question: {req.question}\n\nSources:\n{context}"}],
    )
    return json.loads(resp.choices[0].message.content)

@app.post("/api/tutorial")
def tutorial(req: LearnRequest):
    from openai import OpenAI
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))
    
    prompt = f"""You are an expert professor creating a comprehensive learning tutorial for: {req.faith}.
    Generate a strict JSON payload with the following structure. 
    Do not leave any fields blank. Ensure the quiz has exactly 10 questions.

    {{
        "tradition": "{req.faith}",
        "description": "A 2-sentence overview.",
        "modules": [
            {{"title": "Module 1 Title", "content": "Full 2-3 paragraph tutorial text for this module."}},
            {{"title": "Module 2 Title", "content": "Full 2-3 paragraph tutorial text."}},
            {{"title": "Module 3 Title", "content": "Full 2-3 paragraph tutorial text."}},
            {{"title": "Module 4 Title", "content": "Full 2-3 paragraph tutorial text."}},
            {{"title": "Module 5 Title", "content": "Full 2-3 paragraph tutorial text."}}
        ],
        "faqs": [
            {{"question": "Common question 1?", "answer": "Answer 1."}},
            {{"question": "Common question 2?", "answer": "Answer 2."}},
            {{"question": "Common question 3?", "answer": "Answer 3."}}
        ],
        "quiz": [
            {{"question": "Q1", "options": ["A", "B", "C", "D"], "answer_index": 0}},
            {{"question": "Q2", "options": ["A", "B", "C", "D"], "answer_index": 1}},
            {{"question": "Q3", "options": ["A", "B", "C", "D"], "answer_index": 2}},
            {{"question": "Q4", "options": ["A", "B", "C", "D"], "answer_index": 0}},
            {{"question": "Q5", "options": ["A", "B", "C", "D"], "answer_index": 1}},
            {{"question": "Q6", "options": ["A", "B", "C", "D"], "answer_index": 2}},
            {{"question": "Q7", "options": ["A", "B", "C", "D"], "answer_index": 0}},
            {{"question": "Q8", "options": ["A", "B", "C", "D"], "answer_index": 1}},
            {{"question": "Q9", "options": ["A", "B", "C", "D"], "answer_index": 2}},
            {{"question": "Q10", "options": ["A", "B", "C", "D"], "answer_index": 0}}
        ]
    }}
    """
    
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b", temperature=0.3, response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(resp.choices[0].message.content)

@app.post("/api/interfaith")
def interfaith(req: InterfaithRequest):
    # Retrieve texts from both traditions regarding the specific topic
    verses_a = retrieve(req.topic, [req.faith_a], k_per_faith=3)
    verses_b = retrieve(req.topic, [req.faith_b], k_per_faith=3)
    all_verses = verses_a + verses_b
    
    from openai import OpenAI
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))
    context = "\n".join(f"[{v['faith']} | {v['citation']}] {v['text']}" for v in all_verses)
    
    prompt = f"""You are an empathetic, neutral counselor specializing in interfaith relationships. 
    A user is navigating a relationship involving {req.faith_a} and {req.faith_b}. They are specifically struggling with: {req.topic}.

    Using ONLY the provided primary texts below, create a practical, respectful guide. 
    Do not take sides. Do not water down the differences. Explain the theological 'why' behind each tradition's stance so the user understands their partner/parents.

    Retrieved Texts:
    {context}

    Return strict JSON:
    {{
        "topic": "{req.topic}",
        "faith_a_perspective": "Explain the theological framework of {req.faith_a} regarding this topic.",
        "faith_b_perspective": "Explain the theological framework of {req.faith_b} regarding this topic.",
        "common_ground": "Is there any shared value here? (e.g., both value family, discipline, or compassion).",
        "practical_advice": "3 bullet points on how the user can navigate this specific friction point with respect."
    }}
    """
    
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b", temperature=0.4, response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    data = json.loads(resp.choices[0].message.content)
    data["verses"] = all_verses
    return data

@app.get("/")
def read_root():
    return FileResponse("static/index.html", media_type="text/html")
