import json
import queue
import threading
import time
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from fastapi import FastAPI
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agents.supervisor_agent import supervisor_agent
from tools.pdf_generator import generate_pdf
from utils.gemini import ask_followup

ROOT = Path(__file__).resolve().parents[1]
locations = {
    "tokyo": (35.6762, 139.6503), "japan": (35.6762, 139.6503),
    "paris": (48.8566, 2.3522), "dubai": (25.2048, 55.2708),
    "goa": (15.2993, 74.1240), "london": (51.5072, -0.1276)
}
app = FastAPI(title="Voyager AI", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "web"), name="static")


class TripRequest(BaseModel):
    destination: str = Field(min_length=1, max_length=120, pattern=r".*\S.*")
    days: int = Field(ge=1, le=30)
    budget: str = Field(max_length=120)
    travelers: str = Field(pattern="^(Solo|Couple|Family|Friends)$")
    interests: str = Field(max_length=1500)
    departure: str = Field(max_length=120)


class ChatRequest(BaseModel):
    plan: str = Field(min_length=1, max_length=60000)
    question: str = Field(min_length=1, max_length=2000, pattern=r".*\S.*")


class PdfRequest(BaseModel):
    plan: str = Field(min_length=1, max_length=60000)


@app.get("/")
def home():
    return FileResponse(ROOT / "web" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "model": "gemini-2.5-flash"}


@app.get("/api/location")
def location(destination: str = ""):
    coordinates = locations.get(destination.strip().casefold())
    return {"coordinates": coordinates}


def stream_request(operation):
    messages = queue.Queue()
    cancelled = threading.Event()
    started = time.perf_counter()
    first_text = None

    def update(text):
        nonlocal first_text
        if cancelled.is_set():
            raise RuntimeError("Request cancelled")
        if first_text is None and text.strip():
            first_text = time.perf_counter() - started
        messages.put({"type": "text", "text": text})

    def worker():
        try:
            report = operation(update)
            messages.put({
                "type": "done", "text": report,
                "generation_seconds": round(time.perf_counter() - started, 3),
                "first_text_seconds": round(first_text, 3) if first_text is not None else None
            })
        except Exception as error:
            message = str(error) if isinstance(error, RuntimeError) else "The AI service could not complete this request. Please try again."
            messages.put({"type": "error", "message": message})
        finally:
            messages.put(None)

    def events():
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        try:
            while True:
                try:
                    item = messages.get(timeout=5)
                except queue.Empty:
                    yield json.dumps({"type": "working"}) + "\n"
                    continue
                if item is None:
                    break
                yield json.dumps(item) + "\n"
        finally:
            cancelled.set()

    return StreamingResponse(
        events(), media_type="application/x-ndjson",
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}
    )


@app.post("/api/plan")
def plan(trip: TripRequest):
    return stream_request(lambda update: supervisor_agent(
        trip.destination.strip(), trip.days, trip.budget, trip.travelers,
        trip.interests, trip.departure, on_chunk=update
    ))


@app.post("/api/chat")
def chat(request: ChatRequest):
    return stream_request(lambda update: ask_followup(request.plan, request.question, on_chunk=update))


@app.post("/api/pdf")
def pdf(request: PdfRequest):
    buffer = BytesIO()
    generate_pdf(escape(request.plan), filename=buffer)
    return Response(
        buffer.getvalue(), media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="VoyagerAI_TravelPlan.pdf"'}
    )
