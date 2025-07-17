from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import subprocess
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Get backend URL from environment variable or default to localhost
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:11434")


@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/copilot-chat")
def copilot_chat(user_input: str = Form(...)):
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
        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse({"reply": f"Error: {str(e)}"}, status_code=500)


@app.post("/minikube-run")
async def minikube_run(request: Request):
    data = await request.json()
    command = data.get("command", "")
    if not command or not isinstance(command, str):
        raise HTTPException(status_code=400, detail="Invalid command")

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode().strip()
        if not output:
            output = "[Executed successfully but no output]"
    except subprocess.CalledProcessError as e:
        output = e.output.decode().strip() or "[Error running command]"
    except Exception as e:
        output = f"Unexpected error: {str(e)}"

    return JSONResponse({"output": output})
