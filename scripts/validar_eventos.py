"""Valida as referencias e a cronologia; use --mongo para conferir a carga do servidor."""
from collections import Counter,defaultdict
from datetime import datetime,timezone,timedelta
from decimal import Decimal
from pathlib import Path
import argparse,json
from config import ROOT,MONGODB_URI,connection

def validate(use_mongo=False):
    docs=json.loads((ROOT/'data/eventos_sinteticos.json').read_text(encoding='utf-8'))
    origin='Arquivo JSON incluido no pacote; nao comprova execucao MongoDB.'
    if use_mongo:
        from pymongo import MongoClient
        with MongoClient(MONGODB_URI,serverSelectionTimeoutMS=5000,tz_aware=True) as client:
            docs_db=list(client.varejomix_events.events.find({}, {'_id':0}))
            for d in docs_db:d['event_time']=d['event_time'].isoformat(timespec='milliseconds').replace('+00:00','Z')
            assert sorted(docs,key=lambda d:d['event_id'])==sorted(docs_db,key=lambda d:d['event_id']), 'MongoDB diverge do JSON: recrie a carga da V2.'
        docs=docs_db;origin='MongoDB: conteudo comparado integralmente ao JSON do pacote.'
    with connection() as c:
        orders={r[0]:r[1:] for r in c.execute('SELECT order_id,customer_id,order_ts,total_amount,channel FROM analytics.vw_valid_orders').fetchall()}
        customers=dict(c.execute('SELECT customer_id,created_at FROM oltp.customers').fetchall())
        quantities=dict(c.execute('SELECT order_id,SUM(quantity) FROM oltp.order_items GROUP BY order_id').fetchall())
        products=set(r[0] for r in c.execute('SELECT product_id FROM oltp.products').fetchall())
    sessions=defaultdict(list);ids=set();purchase_ids=set()
    for d in docs:
        assert d['event_id'] not in ids, 'event_id duplicado'
        ids.add(d['event_id']);sessions[d['session_id']].append(d)
        ts=datetime.fromisoformat(d['event_time'].replace('Z','+00:00'))
        cid=d.get('customer_id')
        assert cid is None or (cid in customers and ts>=customers[cid]), 'Evento antes do cadastro ou cliente inexistente'
        assert 'product_id' not in d or d['product_id'] in products, 'Produto inexistente'
        if d['event_name']=='purchase':
            oid=d['order_id'];assert oid in orders,'Pedido inexistente ou nao confirmado'
            expected_cid,order_ts,total,channel=orders[oid]
            assert cid==expected_cid and channel=='ECOMMERCE','Cliente/canal divergente'
            assert order_ts<=ts<=order_ts+timedelta(minutes=10),'Horario divergente'
            assert Decimal(str(d['purchase']['total']))==total,'Valor divergente'
            assert d['purchase']['item_count']==quantities[oid],'Quantidade divergente'
            assert oid not in purchase_ids,'Compra duplicada';purchase_ids.add(oid)
    reach=Counter()
    for events in sessions.values():
        names={e['event_name'] for e in events};reach.update(names)
        assert len({e['session']['source'] for e in events})==1,'Origem muda dentro da sessao'
        stage_times={e['event_name']:e['event_time'] for e in events}
        if 'purchase' in names:
            assert all(k in names for k in ('page_view','add_to_cart','checkout_start'))
            assert stage_times['page_view']<=stage_times['add_to_cart']<=stage_times['checkout_start']<=stage_times['purchase']
    return {'origem':origin,'resultado':'APROVADO','documentos':len(docs),'sessoes':len(sessions),
            'eventos_por_tipo':dict(Counter(d['event_name'] for d in docs)),
            'sessoes_por_etapa':dict(reach),'compras_reconciliadas':len(purchase_ids),
            'conversao_total':reach['purchase']/len(sessions)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mongo',action='store_true');p.add_argument('--output');a=p.parse_args()
    result=json.dumps(validate(a.mongo),ensure_ascii=False,indent=2)+'\n'
    if a.output:
        out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(result,encoding='utf-8')
    print(result)
