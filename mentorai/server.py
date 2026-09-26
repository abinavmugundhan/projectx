"""Optional FastAPI transport around the local index."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from rag import MentorIndex

app = FastAPI(title='MentorAI')
index = MentorIndex()


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
