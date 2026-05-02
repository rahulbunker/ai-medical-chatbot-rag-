from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from connect_llm import get_answer

app = FastAPI(title="Rahul HealthBot")
templates = Jinja2Templates(directory="templates")

class QueryRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/ask")
async def ask_question(query: QueryRequest):
    try:
        answer, sources = get_answer(query.question)
        source_texts = [doc.page_content[:300] for doc in sources]
        return JSONResponse({
            "answer": answer,
            "sources": source_texts,
            "status": "success"
        })
    except Exception as e:
        return JSONResponse({
            "answer": f"Error: {str(e)}",
            "sources": [],
            "status": "error"
        }, status_code=500)

@app.get("/health")
async def health_check():
    return {"status": "Rahul HealthBot is running!"}