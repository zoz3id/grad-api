from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import time
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = "ideas.db"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS ideas (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT NOT NULL,
            title TEXT NOT NULL,
            desc  TEXT NOT NULL,
            ts    INTEGER NOT NULL
        )
    """)
    con.commit()
    con.close()

init_db()

class Idea(BaseModel):
    name:  str
    title: str
    desc:  str

@app.get("/ideas")
def get_ideas():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT id,name,title,desc,ts FROM ideas ORDER BY ts DESC").fetchall()
    con.close()
    return [{"id":r[0],"name":r[1],"title":r[2],"desc":r[3],"ts":r[4]} for r in rows]

@app.post("/ideas")
def add_idea(idea: Idea):
    if not idea.name.strip() or not idea.title.strip() or not idea.desc.strip():
        raise HTTPException(status_code=400, detail="كل الحقول مطلوبة")
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO ideas (name,title,desc,ts) VALUES (?,?,?,?)",
                (idea.name.strip(), idea.title.strip(), idea.desc.strip(), int(time.time()*1000)))
    con.commit()
    con.close()
    return {"ok": True}

@app.get("/")
def root():
    return {"status": "running"}
