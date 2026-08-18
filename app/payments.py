import hashlib,base64,json,uuid
from .config import CLICK_SERVICE_ID,CLICK_MERCHANT_ID,CLICK_SECRET_KEY,PAYME_ID,PAYME_KEY,PUBLIC_BASE_URL
from .db import create_order,get_order,prepare_order,pay_order

def order_id(uid): return f'SA-{uid}-{uuid.uuid4().hex[:12]}'
async def create_payment(uid,amount,provider):
    oid=order_id(uid);await create_order(oid,uid,amount,provider)
    if provider=='click':
        url=f'https://my.click.uz/services/pay?service_id={CLICK_SERVICE_ID}&merchant_id={CLICK_MERCHANT_ID}&amount={amount}&transaction_param={oid}'
    else:
        payload={'m':'Payme','ac':{'order_id':oid},'a':amount*100,'c':PUBLIC_BASE_URL+'/payment/success'}
        url='https://checkout.paycom.uz/'+base64.b64encode(json.dumps(payload,separators=(',',':')).encode()).decode()
    return oid,url

def click_sig_prepare(d):
    s=str(d['click_trans_id'])+str(d['service_id'])+CLICK_SECRET_KEY+str(d['merchant_trans_id'])+str(d['amount'])+str(d['action'])+str(d['sign_time']);return hashlib.md5(s.encode()).hexdigest()
def click_sig_complete(d):
    s=str(d['click_trans_id'])+str(d['service_id'])+CLICK_SECRET_KEY+str(d['merchant_trans_id'])+str(d['merchant_prepare_id'])+str(d['amount'])+str(d['action'])+str(d['sign_time']);return hashlib.md5(s.encode()).hexdigest()
async def click_callback(d):
    oid=str(d.get('merchant_trans_id',''));o=await get_order(oid)
    if not o:return {'error':-5,'error_note':'Order not found'}
    if int(float(d.get('amount',0)))!=o[2]:return {'error':-2,'error_note':'Incorrect amount'}
    if str(d.get('service_id'))!=str(CLICK_SERVICE_ID):return {'error':-1,'error_note':'Service ID mismatch'}
    action=int(d.get('action',-1))
    if action==0:
        if click_sig_prepare(d)!=str(d.get('sign_string','')).lower():return {'error':-1,'error_note':'SIGN CHECK FAILED!'}
        await prepare_order(oid,d['click_trans_id']);return {'click_trans_id':d['click_trans_id'],'merchant_trans_id':oid,'merchant_prepare_id':d['click_trans_id'],'error':0,'error_note':'Success'}
    if action==1:
        if click_sig_complete(d)!=str(d.get('sign_string','')).lower():return {'error':-1,'error_note':'SIGN CHECK FAILED!'}
        if str(d.get('error','0'))!='0':return {'error':-9,'error_note':'Transaction cancelled'}
        await pay_order(oid,d['click_trans_id']);return {'click_trans_id':d['click_trans_id'],'merchant_trans_id':oid,'merchant_confirm_id':d['click_trans_id'],'error':0,'error_note':'Success'}
    return {'error':-3,'error_note':'Action not found'}

def payme_auth(auth):
    if not auth.startswith('Basic '):return False
    try:
        a=base64.b64decode(auth[6:]).decode();u,p=a.split(':',1);return u==PAYME_ID and p==PAYME_KEY
    except:return False
async def payme_callback(req):
    rid=req.get('id');m=req.get('method');p=req.get('params') or {};a=p.get('account') or {};oid=str(a.get('order_id',''));o=await get_order(oid)
    def ok(result):return {'jsonrpc':'2.0','id':rid,'result':result}
    def err(code,msg):return {'jsonrpc':'2.0','id':rid,'error':{'code':code,'message':{'uz':msg,'ru':msg}}}
    if not o:return err(-31050,'Buyurtma topilmadi')
    if int(p.get('amount',0))!=o[2]*100:return err(-31001,'Summa noto\'g\'ri')
    if m=='CheckPerformTransaction':return ok({'allow':True})
    if m=='CreateTransaction':await prepare_order(oid,p.get('id'));return ok({'create_time':p.get('time',0),'transaction':oid,'state':1})
    if m=='PerformTransaction':await pay_order(oid,p.get('id'));return ok({'transaction':oid,'perform_time':p.get('time',0),'state':2})
    if m=='CheckTransaction':return ok({'create_time':0,'perform_time':0,'cancel_time':0,'transaction':oid,'state':2 if o[4]=='paid' else 1,'reason':None})
    if m=='CancelTransaction':return ok({'transaction':oid,'cancel_time':p.get('time',0),'state':-1})
    return err(-32601,'Method not found')
