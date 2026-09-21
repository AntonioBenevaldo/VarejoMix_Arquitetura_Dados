"""Extracao real PostgreSQL -> features RFM -> CSV/Parquet com manifesto e auditoria."""
from datetime import datetime,timezone
from pathlib import Path
from hashlib import sha256
import json,os,platform,shutil,uuid
import pandas as pd
import numpy as np
from sqlalchemy import create_engine,text
from sqlalchemy.pool import NullPool
from config import ROOT,DATABASE_URL,CUTOFF_DATE,connection

DICTIONARY=[
('customer_id','inteiro','Identificador tecnico sintetico; nao e uma anonimizacao aplicada a dados reais.'),
('recency_days','inteiro','Dias UTC desde a ultima venda confirmada anterior ao corte.'),
('frequency_365d','inteiro','Vendas confirmadas na janela [corte-365 dias, corte).'),
('monetary_365d','decimal BRL','Soma dos totais liquidos na janela historica.'),
('average_ticket','decimal BRL','Valor medio por venda confirmada na janela.'),
('ecommerce_share','decimal 0 a 1','Proporcao de vendas confirmadas no e-commerce.'),
('distinct_categories','inteiro','Categorias distintas nos itens da janela historica.'),
('repurchase_90d','binario','1 se existe venda confirmada em [corte, corte+90 dias); senao 0.'),
('r_score','inteiro 1 a 3','Escore de recencia: menor recencia recebe maior escore; empates iguais.'),
('f_score','inteiro 1 a 3','Escore da posicao percentual da frequencia; empates iguais.'),
('m_score','inteiro 1 a 3','Escore da posicao percentual do gasto; empates iguais.'),
('rfm_score','inteiro 3 a 9','Soma r_score + f_score + m_score.'),
('segment','categoria','Manutencao (3-4), Potencial (5-6), Alto valor (7-9).')]

def extract(cutoff=CUTOFF_DATE):
    cutoff=pd.Timestamp(cutoff,tz='UTC')
    engine=create_engine(DATABASE_URL,poolclass=NullPool,connect_args={'options':'-c timezone=UTC','connect_timeout':10})
    try:
        with engine.connect() as c:
            c.execute(text("SET TIME ZONE 'UTC'"))
            limits=c.execute(text('SELECT MIN(order_ts),MAX(order_ts) FROM oltp.orders')).one()
            version=c.execute(text('SELECT version()')).scalar_one()
            if limits[1] is None: raise ValueError('A carga PostgreSQL esta vazia.')
            if cutoff+pd.Timedelta(days=90)>pd.Timestamp(limits[1]).normalize()+pd.Timedelta(days=1):
                raise ValueError('A base nao cobre os 90 dias do alvo. Use o corte 2025-10-01 nesta carga.')
            df=pd.read_sql(text((ROOT/'sql/08_features.sql').read_text(encoding='utf-8')),c,params={'cutoff':cutoff.isoformat()})
    finally: engine.dispose()
    if df.empty: raise ValueError('Nenhum cliente elegivel para a data de corte.')
    assert df.customer_id.is_unique and not df.isna().any().any()
    assert df.repurchase_90d.isin([0,1]).all()
    assert (df.recency_days>=1).all() and (df.frequency_365d>=1).all()
    assert df.ecommerce_share.between(0,1).all()
    context={'cutoff_utc':cutoff.isoformat(),'feature_window_days':365,'target_window_days':90,
        'source_min_order_ts':limits[0].isoformat(),'source_max_order_ts':limits[1].isoformat(),
        'server_version':version,'extraction':'PostgreSQL via SQLAlchemy/pandas.read_sql',
        'validation_context':os.getenv('VALIDATION_CONTEXT','Execucao local do usuario'),
        'assumptions':['Vendas confirmadas: PAID/SHIPPED/DELIVERED com pagamento APPROVED integral.',
        'Limites historicos e do alvo sao inclusivo no inicio e exclusivo no fim, em UTC.',
        'Base sintetica com atividade a partir de dezembro/2024; janela de 365 dias usa os registros disponiveis.',
        'Status e categorias sao do snapshot carregado; historico de alteracoes nao foi implementado.']}
    return df,context

def segment(df):
    df=df.copy()
    for source,target in [('recency_days','r_score'),('frequency_365d','f_score'),('monetary_365d','m_score')]:
        score=np.ceil(df[source].rank(method='average',pct=True)*3).clip(1,3).astype(int)
        df[target]=4-score if target=='r_score' else score
    df['rfm_score']=df[['r_score','f_score','m_score']].sum(axis=1)
    df['segment']=pd.cut(df.rfm_score,bins=[0,4,6,9],labels=['Manutencao','Potencial','Alto valor'])
    assert not df.isna().any().any()
    return df

def dictionary():return pd.DataFrame(DICTIONARY,columns=['campo','tipo','descricao'])

def code_hash():
    h=sha256()
    for folder in ['sql','scripts']:
        for p in sorted((ROOT/folder).glob('*')):
            if p.suffix in ('.py','.sql'):h.update(p.name.encode());h.update(p.read_bytes())
    return h.hexdigest()

def export(df,context):
    assert set(df.columns)==set(dictionary().campo),'Dicionario incompleto'
    run_id=str(uuid.uuid4());started=datetime.now(timezone.utc)
    out=ROOT/'outputs'/'execucoes'/run_id;out.mkdir(parents=True,exist_ok=False)
    csv=out/'customer_repurchase_features.csv';parquet=out/'customer_repurchase_features.parquet'
    code=code_hash()
    with connection() as c:
        c.execute('''INSERT INTO audit.pipeline_runs(run_id,pipeline_name,started_at,status,
            source_period_start,source_period_end,input_rows,code_version)
            VALUES (%s,'customer_repurchase_features',%s,'RUNNING',%s,%s,%s,%s)''',
            (run_id,started,pd.Timestamp(context['cutoff_utc'])-pd.Timedelta(days=365),
             pd.Timestamp(context['cutoff_utc'])+pd.Timedelta(days=90),int(df.frequency_365d.sum()),code[:40]))
    try:
        df.to_csv(csv,index=False,lineterminator='\n');df.to_parquet(parquet,index=False)
        csv_hash=sha256(csv.read_bytes()).hexdigest();parquet_hash=sha256(parquet.read_bytes()).hexdigest()
        pd.testing.assert_frame_equal(pd.read_csv(csv),pd.read_parquet(parquet),check_dtype=False,check_categorical=False)
        meta={**context,'run_id':run_id,'started_at_utc':started.isoformat(),'finished_at_utc':datetime.now(timezone.utc).isoformat(),
            'code_sha256':code,'dataset_version':'sha256:'+csv_hash,'csv_sha256':csv_hash,'parquet_sha256':parquet_hash,
            'shape':list(df.shape),'nulls':int(df.isna().sum().sum()),'duplicate_customers':int(df.customer_id.duplicated().sum()),
            'target_counts':{str(k):int(v) for k,v in df.repurchase_90d.value_counts().sort_index().items()},
            'snapshot_directory':out.relative_to(ROOT).as_posix(),'python_version':platform.python_version(),
            'pandas_version':pd.__version__,'project_version':(ROOT/'VERSION').read_text().strip()}
        (out/'manifesto.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        dictionary().to_csv(out/'dicionario_dados.csv',index=False)
        for p in out.iterdir():shutil.copy2(p,ROOT/'outputs'/p.name)
        with connection() as c:
            c.execute('''UPDATE audit.pipeline_runs SET status='SUCCESS',finished_at=%s,output_rows=%s,dataset_version=%s
                WHERE run_id=%s''',(datetime.now(timezone.utc),len(df),meta['dataset_version'],run_id))
        return meta
    except Exception as exc:
        with connection() as c:
            c.execute("UPDATE audit.pipeline_runs SET status='FAILED',finished_at=%s,error_message=%s WHERE run_id=%s",
                      (datetime.now(timezone.utc),type(exc).__name__,run_id))
        raise

if __name__=='__main__':
    df,ctx=extract();df=segment(df);meta=export(df,ctx)
    print(json.dumps(meta,ensure_ascii=False,indent=2))
