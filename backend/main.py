# backend/main.py
import os
import httpx
import re
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from . import models, database
from settings import *
models.Base.metadata.create_all(bind=database.engine)

GITHUB_CLIENT_ID = "Ov23lickgvOZjdGHhNaR"
GITHUB_CLIENT_SECRET = "8d9840129a61aafd04ed3457c460b1a0caf557f9"

app = FastAPI(title="Arcodeum API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/auth/github")
async def github_auth():
    """Redirects the user to GitHub for authentication."""
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}"
    )

@app.get("/auth/github/callback")
async def github_auth_callback(code: str, db: Session = Depends(get_db)):
    """Handles the callback from GitHub and gets the user's access token."""
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
    }
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:

        response = await client.post(
            "https://github.com/login/oauth/access_token",
            params=params,
            headers=headers,
        )
        token_data = response.json()
        access_token = token_data.get("access_token")

        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"},
        )
        user_data = user_response.json()
    return {"token": user_data["login"]}

@app.post("/webhooks/github")
async def handle_github_webhook(request: Request, project_id: int, db: Session = Depends(get_db)):
    payload = await request.json()
    
    task_id_pattern = re.compile(r'\[ARC-(\d+)\]')
    
    if 'commits' in payload:
        for commit in payload['commits']:
            message = commit.get('message', '')
            found_ids = task_id_pattern.findall(message)
            for task_num in found_ids:
                task_id_str_to_find = f"ARC-{task_num}"
                task_to_update = db.query(models.Task).filter(models.Task.task_id_str == task_id_str_to_find).first()
                if task_to_update and task_to_update.project_id == project_id:
                    task_to_update.status = "Done"
                    db.commit()

    return {"status": "processed"}

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    """Serves the main index.html file."""
    return templates.TemplateResponse("index.html", {"request": request})
