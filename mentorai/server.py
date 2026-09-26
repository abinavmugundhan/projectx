"""Optional FastAPI transport around the local index."""
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
import os
from pydantic import BaseModel, Field
from rag import MentorIndex

app = FastAPI(title='MentorAI')
index = MentorIndex(os.getenv("MENTOR_DB", "mentorai.sqlite3"))


class Document(BaseModel):
    name: str = Field(min_length=1)
    text: str = Field(min_length=1)


class Question(BaseModel):
    question: str = Field(min_length=1)


@app.post('/documents')
def add_document(doc: Document):
    index.add(doc.name, doc.text)
    return {'indexed': doc.name}


@app.post('/ask')
def ask(query: Question):
    return index.answer(query.question)


@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/')
def home():
    return FileResponse(Path(__file__).with_name('index.html'))
