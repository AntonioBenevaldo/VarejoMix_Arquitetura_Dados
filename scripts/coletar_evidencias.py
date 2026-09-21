"""Roda as validacoes e o notebook; captura evidencias do Docker local."""
import json,subprocess,sys
from pathlib import Path
from config import ROOT
from executar_sql import executar
from validar_eventos import validate
from executar_mongo import executar_consultas_mongo

def run(args,input=None):
    result=subprocess.run(args,input=input,cwd=ROOT,capture_output=True)
    if result.returncode:
        print(result.stderr.decode('utf-8',errors='replace'))
        print(result.stdout.decode('utf-8',errors='replace'))
        raise RuntimeError('Comando falhou: '+' '.join(args))
    return result.stdout.decode('utf-8',errors='replace') + result.stderr.decode('utf-8',errors='replace')

def main():
    out=ROOT/'evidencias/local';out.mkdir(parents=True,exist_ok=True)
    print('1/6 Conferindo os servicos Docker...')
    (out/'docker_compose_ps.txt').write_text(run(['docker','compose','ps']),encoding='utf-8')
    print('2/6 Validando SQL e executando consultas...')
    for name in ['06_validacoes','04_queries','05_index_explain']:
        executar('sql/'+name+'.sql',out/(name+'.txt'))
    (out/'testes_regressao.txt').write_text(run([sys.executable,'-m','unittest','discover','-s','tests','-v']),encoding='utf-8')
    print('3/6 Reconciliando eventos MongoDB com PostgreSQL...')
    (out/'eventos_reconciliados.json').write_text(json.dumps(validate(True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('4/6 Executando o funil e os planos MongoDB...')
    executar_consultas_mongo(ROOT, out/'mongo_local.txt')
    print('5/6 Executando notebook conectado ao PostgreSQL...')
    run([sys.executable,'-m','nbconvert','--to','notebook','--execute','--inplace',
         '--ExecutePreprocessor.timeout=180','notebooks/analise_recompra.ipynb'])
    nbpath=ROOT/'notebooks/analise_recompra.ipynb'
    nb=json.loads(nbpath.read_text(encoding='utf-8'))
    nb.setdefault('metadata',{})['validation']={'method':'Executado por Jupyter nbconvert; SQL e reconciliacao MongoDB local aprovados.'}
    nbpath.write_text(json.dumps(nb,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
    run([sys.executable,'-m','nbconvert','--to','html','--output','notebook_executado.html',
         '--output-dir',str(out),'notebooks/analise_recompra.ipynb'])
    print('6/6 Conferindo contagens e salvando auditoria...')
    executar('sql/07_contagens.sql',out/'07_contagens.txt')
    from config import connection
    with connection() as c:
        rows=c.execute('SELECT run_id,pipeline_name,status,output_rows,dataset_version FROM audit.pipeline_runs ORDER BY started_at').fetchall()
    (out/'auditoria.json').write_text(json.dumps(rows,default=str,indent=2)+'\n',encoding='utf-8')
    print('APROVADO: evidencias em evidencias/local; dataset em outputs; notebook atualizado.')

if __name__=='__main__':main()
