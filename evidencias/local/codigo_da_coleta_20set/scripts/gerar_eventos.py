"""Gera eventos coerentes a partir dos pedidos reais da carga PostgreSQL.
Uso opcional: python scripts/gerar_eventos.py (antes de reinicializar o MongoDB).
O ZIP ja inclui os arquivos gerados; o comando nao importa no MongoDB.
"""
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json, random
from config import ROOT, connection

def generate():
    rng=random.Random(20251231)
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''SELECT o.order_id,o.customer_id,o.order_ts,o.total_amount,
                (SELECT SUM(quantity) FROM oltp.order_items WHERE order_id=o.order_id) AS item_count,
                i.product_id,i.unit_price
                FROM analytics.vw_valid_orders o
                JOIN oltp.customers c USING(customer_id)
                JOIN oltp.order_items i ON i.order_id=o.order_id AND i.line_number=1
                WHERE o.channel='ECOMMERCE'
                  AND o.order_ts >= '2025-12-15T00:00:00Z'
                  AND o.order_ts < '2025-12-30T00:00:00Z'
                  AND o.order_ts > c.created_at + INTERVAL '10 minutes'
                ORDER BY o.order_id''')
            rows=cur.fetchall()
    if len(rows)<78: raise ValueError('A carga precisa de ao menos 78 vendas digitais elegiveis.')
    purchases=rng.sample(rows,78)
    docs=[]
    def add(sid,name,t,customer,source,**extra):
        docs.append(dict(event_id=f'evt-{len(docs)+1:06d}',schema_version=1,
            event_name=name,event_time=t.isoformat(timespec='milliseconds').replace('+00:00','Z'),
            session_id=sid,customer_id=customer,
            device={'type':'mobile','os':'Android'},
            session={'source':source,'campaign':None},**extra))
    for n in range(500):
        sid=f'ses-{n+1:05d}'
        source=rng.choice(['organic','paid','direct','email'])
        if n<78:
            oid,cid,ts,total,qty,pid,price=purchases[n]
            t=ts-timedelta(minutes=8)
        else:
            oid=None;cid=None
            t=datetime(2025,12,15,tzinfo=timezone.utc)+timedelta(days=rng.randrange(15),hours=10,minutes=rng.randrange(40))
            pid=rng.randrange(1,41);price=Decimal('35')+Decimal('5.40')*pid
            qty=1;total=price
        add(sid,'page_view',t,cid,source,page={'url':'/catalogo','referrer':source})
        if n%3==0:add(sid,'search',t+timedelta(minutes=1),cid,source,search={'term':'produto sintetico','result_count':40})
        if n<220:
            add(sid,'add_to_cart',t+timedelta(minutes=3),cid,source,product_id=int(pid),
                product_context={'sku':f'SKU-{pid:04d}','displayed_price':float(price)})
        if n<123:
            add(sid,'checkout_start',t+timedelta(minutes=6),cid,source,
                cart={'item_count':int(qty),'displayed_total':float(total)})
        if n<78:
            add(sid,'purchase',ts+timedelta(minutes=5),cid,source,order_id=int(oid),
                purchase={'item_count':int(qty),'total':float(total),'currency':'BRL'})
    return docs

def js_value(v,key=''):
    if key=='event_time':return 'ISODate('+json.dumps(v)+')'
    if v is None:return 'null'
    if isinstance(v,str):return json.dumps(v,ensure_ascii=False)
    if isinstance(v,int):return f'NumberLong({v})' if key in ('customer_id','order_id','product_id') else f'NumberInt({v})'
    if isinstance(v,float):return repr(v)
    if isinstance(v,dict):return '{'+', '.join(json.dumps(k)+': '+js_value(x,k) for k,x in v.items())+'}'
    raise TypeError(type(v))

if __name__=='__main__':
    docs=generate()
    (ROOT/'data/eventos_sinteticos.json').write_text(json.dumps(docs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['// Gerado por scripts/gerar_eventos.py a partir do PostgreSQL corrigido.',
           'db = db.getSiblingDB("varejomix_events");']
    for i in range(0,len(docs),250):
        lines.append('db.events.insertMany([\n'+',\n'.join(js_value(d) for d in docs[i:i+250])+'\n]);')
    (ROOT/'nosql/02-eventos-sinteticos.js').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    sample=[d for d in docs if d['session_id']=='ses-00001']
    (ROOT/'nosql/exemplos_eventos.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Eventos:',len(docs),'Sessoes:',len({d['session_id'] for d in docs}),'Tipos:',dict(Counter(d['event_name'] for d in docs)))
