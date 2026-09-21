"""Executa SQL e salva evidencias UTF-8 em Windows, Linux e macOS."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
from config import ROOT, connection

def executar(path, output=None):
    path = Path(path)
    if not path.is_absolute(): path = ROOT / path
    sql = path.read_text(encoding='utf-8-sig')
    if any(line.lstrip().startswith('\\') for line in sql.splitlines()):
        raise ValueError('Use SQL puro neste executor; metacomandos psql nao sao aceitos.')
    parts = [f'Arquivo: {path.name}', f'Executado em UTC: {datetime.now(timezone.utc).isoformat()}']
    with connection() as conn:
        parts.append('Servidor: ' + conn.execute('SELECT version()').fetchone()[0])
        with conn.cursor() as cur:
            cur.execute(sql, prepare=False)
            while True:
                if cur.description:
                    parts.append(' | '.join(x.name for x in cur.description))
                    rows=cur.fetchall()
                    parts.extend(' | '.join('NULL' if v is None else str(v) for v in row) for row in rows)
                    parts.append(f'({len(rows)} linhas)')
                elif cur.statusmessage: parts.append(cur.statusmessage)
                if not cur.nextset(): break
    result='\n'.join(parts)+'\n'
    if output:
        output=Path(output)
        if not output.is_absolute(): output=ROOT/output
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(result,encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('sql');p.add_argument('--output');a=p.parse_args()
    print(executar(a.sql,a.output))
