"""Small local-first, source-cited retrieval engine with SQLite persistence."""
import math
import re
import sqlite3
from collections import Counter
from pathlib import Path


def tokens(text):
    return re.findall(r'[\w\u0b80-\u0bff]+', text.lower())


def chunks(text, size=600, overlap=100):
    if size <= overlap or overlap < 0:
        raise ValueError('size must exceed nonnegative overlap')
    return [text[i:i + size] for i in range(0, len(text), size - overlap) if text[i:i + size].strip()]


class MentorIndex:
    def __init__(self, path='mentorai.sqlite3'):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute('CREATE TABLE IF NOT EXISTS passages (source TEXT, ordinal INTEGER, body TEXT, PRIMARY KEY(source, ordinal))')
        self.db.commit()

    def add(self, name, content):
        if not name or not content.strip():
            raise ValueError('source and text required')
        self.db.execute('DELETE FROM passages WHERE source=?', (name,))
        self.db.executemany('INSERT INTO passages VALUES (?, ?, ?)',
                            ((name, i, part) for i, part in enumerate(chunks(content))))
        self.db.commit()

    def search(self, query, limit=4):
        terms = set(tokens(query))
        if not terms:
            return []
        rows = self.db.execute('SELECT source, ordinal, body FROM passages').fetchall()
        if not rows:
            return []
        doc_freq = Counter(t for _, _, body in rows for t in set(tokens(body)))
        scores = []
        for source, ordinal, body in rows:
            counts = Counter(tokens(body))
            score = sum((1 + math.log(counts[t])) * math.log(1 + (len(rows) + 1) / (doc_freq[t] + 1))
                        for t in terms if counts[t])
            if score:
                scores.append((score, source, ordinal, body))
        scores.sort(key=lambda item: (-item[0], item[1], item[2]))
        return [{'source': s, 'chunk': i, 'text': body, 'score': round(score, 3)}
                for score, s, i, body in scores[:limit]]

    def answer(self, question):
        hits = self.search(question)
        if not hits:
            return {'answer': 'I could not find support for that in the indexed documents.', 'sources': []}
        # Extractive answer stays grounded even without an LLM.
        terms = set(tokens(question))
        sentences = re.split(r'(?<=[.!?])\s+', hits[0]['text'])
        best = max(sentences, key=lambda s: len(terms & set(tokens(s))))
        return {'answer': best[:500], 'sources': [{'source': h['source'], 'chunk': h['chunk']} for h in hits]}
