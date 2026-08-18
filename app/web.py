from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import JSONResponse,HTMLResponse
from .payments import click_callback,payme_callback,payme_auth
app=FastAPI(title='SlaydAI Pro Payments')
@app.get('/health')
async def health():return {'status':'ok'}
@app.get('/payment/success')
async def success():return HTMLResponse('<h2>To\'lov qabul qilindi. Telegram botga qayting.</h2>')
@app.post('/payments/click')
async def click(request:Request):return JSONResponse(await click_callback(dict(await request.form())))
@app.post('/payments/payme')
async def payme(request:Request):
    if not payme_auth(request.headers.get('Authorization','')):raise HTTPException(401,'Unauthorized')
    return JSONResponse(await payme_callback(await request.json()))
