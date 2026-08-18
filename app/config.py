import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN=os.getenv('BOT_TOKEN','')
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY','')
OPENAI_MODEL=os.getenv('OPENAI_MODEL','gpt-4.1-mini')
ADMIN_IDS={int(x.strip()) for x in os.getenv('ADMIN_IDS','').split(',') if x.strip().isdigit()}
PUBLIC_BASE_URL=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
CLICK_SERVICE_ID=os.getenv('CLICK_SERVICE_ID','')
CLICK_MERCHANT_ID=os.getenv('CLICK_MERCHANT_ID','')
CLICK_SECRET_KEY=os.getenv('CLICK_SECRET_KEY','')
PAYME_ID=os.getenv('PAYME_ID','')
PAYME_KEY=os.getenv('PAYME_KEY','')
FREE_GENERATIONS = 2
GENERATION_PRICE_UZS=int(os.getenv('GENERATION_PRICE_UZS','4000'))
REFERRAL_BONUS_UZS=int(os.getenv('REFERRAL_BONUS_UZS','1000'))
BOT_NAME=os.getenv('BOT_NAME','SlaydAI Pro')
DB_PATH='slaydai.db'
