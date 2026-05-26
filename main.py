import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="CBIT Career Hub Backend")

# Security Bypass Logic
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            package TEXT NOT NULL,
            skills TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

class JobSchema(BaseModel):
    company: str
    role: str
    package: str
    skills: str
    status: str

class JobResponse(BaseModel):
    id: int
    company: str
    role: str
    package: str
    skills: str
    status: str

@app.get("/api/jobs", response_model=List[JobResponse])
def get_jobs():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, company, role, package, skills, status FROM jobs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "company": r[1], "role": r[2], "package": r[3], "skills": r[4], "status": r[5]} for r in rows]

@app.post("/api/jobs", response_model=JobResponse)
def add_job(job: JobSchema):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO jobs (company, role, package, skills, status) VALUES (?, ?, ?, ?, ?)",
            (job.company, job.role, job.package, job.skills, job.status)
        )
        conn.commit()
        job_id = cursor.lastrowid
        conn.close()
        return {"id": job_id, **job.model_dump()}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)