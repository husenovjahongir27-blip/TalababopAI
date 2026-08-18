# SlaydAI Pro — Click + Payme

GitHub-ready Telegram AI bot with a FastAPI payment server.

## Functions
- Slayd -> PPTX
- Mustaqil ish, kurs ishi, referat, maqola, konspekt, tezis, glossariy, test -> DOCX
- AI helper
- Shorten / rewrite / translate / outline
- Profile, balance, referral, history
- Click and Payme payment orders
- Automatic payment callback -> user balance
- Admin statistics and manual balance

## Project layout
app/
  config.py
  db.py
  handlers.py
  payments.py
  services.py
  web.py
  main.py
requirements.txt
render.yaml
.env.example

## Local test
1. Python 3.11+
2. `python -m venv .venv`
3. Activate it
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env`
6. Fill BOT_TOKEN and OPENAI_API_KEY
7. `python -m app.main`

## Production
Push this project to a PRIVATE GitHub repository and connect the repository to Render.
Render runs `python -m app.main` and exposes `/health` and the payment callback endpoints.

## Payment callback URLs
After Render gives a public HTTPS domain, configure:
- Click: `https://YOUR-DOMAIN/payments/click`
- Payme: `https://YOUR-DOMAIN/payments/payme`

The exact merchant settings and credentials must come from your Click Business / Payme Business accounts. Never commit them to GitHub.

## Security
- Do not upload `.env`.
- Do not upload `__pycache__` or `.pyc`.
- Keep the repository private.
