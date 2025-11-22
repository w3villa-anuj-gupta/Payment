from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import razorpay
from pathlib import Path

app = FastAPI()

# Get the base directory correctly for both local and Vercel environments
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Only mount static files if the directory exists (for serverless compatibility)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "rzp_test_your_key")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "your_secret")
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

MOVIES = [
    {"id": 1, "title": "The Great Adventure", "price": 250},
    {"id": 2, "title": "Romantic Saga", "price": 199},
    {"id": 3, "title": "Sci-Fi Thriller", "price": 350},
]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "movies": MOVIES, "key_id": RAZORPAY_KEY_ID})


@app.post("/create_order")
async def create_order(payload: dict):
    try:
        movie_id = int(payload.get("movie_id"))
        qty = int(payload.get("qty", 1))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    movie = next((m for m in MOVIES if m["id"] == movie_id), None)
    if not movie:
        raise HTTPException(status_code=400, detail="Invalid movie id")

    amount = movie["price"] * qty * 100
    order_data = {
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1",
        "notes": {"movie": movie["title"], "qty": str(qty)},
    }

    order = client.order.create(data=order_data)
    return JSONResponse({"order_id": order["id"], "amount": amount, "currency": "INR", "key": RAZORPAY_KEY_ID})


@app.post("/verify")
async def verify(payload: dict):
    params = {
        "razorpay_order_id": payload.get("razorpay_order_id"),
        "razorpay_payment_id": payload.get("razorpay_payment_id"),
        "razorpay_signature": payload.get("razorpay_signature"),
    }

    if not all(params.values()):
        raise HTTPException(status_code=400, detail="Missing payment parameters")

    try:
        client.utility.verify_payment_signature(params)
    except Exception:
        raise HTTPException(status_code=400, detail="Signature verification failed")

    return JSONResponse({"status": "success", "payment_id": params["razorpay_payment_id"]})


@app.get("/success", response_class=HTMLResponse)
async def success(request: Request):
    payment_id = request.query_params.get("payment_id")
    return templates.TemplateResponse("success.html", {"request": request, "payment_id": payment_id})
