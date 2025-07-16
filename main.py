from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import json
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Get backend URL from environment variable or default to container name
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:11434")

@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
def chat(request: Request, user_input: str = Form(...)):
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": user_input,
                "stream": False
            }
        )
        response.raise_for_status()
        data = response.json()
        reply = data.get("response", "").strip()
        html_reply = reply.replace("\n", "<br>")
        formatted_reply = f"""
        <div class="response-container">
            <p>{html_reply}</p>
        </div>
        """
    except Exception as e:
        formatted_reply = f"<p>Error: {str(e)}</p>"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user_input": user_input,
        "response": formatted_reply
    })
