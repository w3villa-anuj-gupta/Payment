from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import stripe
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Get the base directory correctly for both local and Vercel environments
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Only mount static files if the directory exists (for serverless compatibility)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_your_secret_key")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "pk_test_your_publishable_key")

MOVIES = [
    {"id": 1, "title": "The Great Adventure", "price": 250},
    {"id": 2, "title": "Romantic Saga", "price": 199},
    {"id": 3, "title": "Sci-Fi Thriller", "price": 350},
]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "movies": MOVIES,
        "stripe_key": STRIPE_PUBLISHABLE_KEY
    })


@app.post("/create-checkout-session")
async def create_checkout_session(payload: dict):
    try:
        movie_id = int(payload.get("movie_id"))
        qty = int(payload.get("qty", 1))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    movie = next((m for m in MOVIES if m["id"] == movie_id), None)
    if not movie:
        raise HTTPException(status_code=400, detail="Invalid movie id")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": movie["title"],
                            "description": f"Movie Ticket x{qty}",
                        },
                        "unit_amount": movie["price"] * 100,
                    },
                    "quantity": qty,
                }
            ],
            mode="payment",
            success_url="http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:8000/cancel",
            metadata={"movie": movie["title"], "qty": str(qty)},
        )
        return JSONResponse({"url": session.url, "session_id": session.id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/success", response_class=HTMLResponse)
async def success(request: Request):
    session_id = request.query_params.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        payment_id = session.payment_intent
        return templates.TemplateResponse("success.html", {
            "request": request,
            "payment_id": payment_id,
            "amount": session.amount_total / 100
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/cancel", response_class=HTMLResponse)
async def cancel(request: Request):
    return templates.TemplateResponse("cancel.html", {"request": request})
