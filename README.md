# Movie Ticket Purchase (Razorpay + FastAPI)

Small demo app showing a movie ticket purchase flow using FastAPI (backend) and a minimal HTML/CSS/JS frontend integrated with Razorpay Checkout.

Prerequisites
- Python 3.9+
- A Razorpay account and API keys (test keys are fine for development)

Setup
1. Create a virtualenv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set environment variables (replace with your keys):

```bash
export RAZORPAY_KEY_ID=rzp_test_your_key
export RAZORPAY_KEY_SECRET=your_secret
```

Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` and try purchasing a ticket. Payments made with test keys will be in Razorpay's test dashboard.

Deploy to Vercel

1. Push your project to GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

2. Connect to Vercel:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project" → Select your GitHub repo
   - Vercel auto-detects Python and uses `vercel.json`
   - Under "Environment Variables", add:
     - `RAZORPAY_KEY_ID=rzp_test_your_key`
     - `RAZORPAY_KEY_SECRET=your_secret`
   - Click "Deploy"

3. Once deployed, Vercel assigns a URL (e.g., `https://your-app.vercel.app`). Use Razorpay test keys for development.

Notes
- This is a demo; adapt server-side verification, order persistence, and security before using in production.
- For production, use Razorpay live keys and enable webhook verification.
- Vercel's free tier includes generous serverless function limits.
