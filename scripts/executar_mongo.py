"""Executa o JavaScript completo em mongosh --file e rejeita saidas parciais."""
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
import tempfile
import uuid

MARCADOR = 'VAREJOMIX_MONGO_CONSULTAS_CONCLUIDAS'
ERROS = re.compile(r'Invalid REPL keyword|\bUncaught\b|\b(?:Type|Syntax|Reference|MongoServer|MongoNetwork)Error\b')


def validar_saida(texto, returncode):
    if returncode != 0 or ERROS.search(texto) or MARCADOR not in texto.splitlines():
        raise RuntimeError('Consultas MongoDB incompletas ou com erro; confira evidencias/local/mongo_local.txt.')


def executar_consultas_mongo(root, output):
    root, output = Path(root), Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    inicio = datetime.now(timezone.utc).isoformat()
    remoto = '/tmp/varejomix_funil_' + uuid.uuid4().hex + '.js'
    script = (root / 'nosql/03-consultas_funil.js').read_text(encoding='utf-8-sig')
    # O marcador so aparece depois de todas as consultas. A excecao encerra mongosh.
    protegido = ('try {\n' + script + '\nprint("' + MARCADOR + '");\n'
                 '} catch (erro) {\nconsole.error(erro.stack || String(erro));\nexit(1);\n}\n')
    cabecalho = 'Executado em UTC: ' + inicio + '\nModo: mongosh --file\n'
    try:
        with tempfile.TemporaryDirectory(prefix='varejomix_mongo_') as tmp:
            local = Path(tmp) / 'consultas.js'
            local.write_text(protegido, encoding='utf-8')
            copia = subprocess.run(['docker', 'compose', 'cp', str(local), 'mongodb:' + remoto],
                                   cwd=root, capture_output=True)
            if copia.returncode:
                saida = (copia.stdout + copia.stderr).decode('utf-8', errors='replace')
                output.write_text(cabecalho + saida, encoding='utf-8')
                raise RuntimeError('Falha ao copiar o script para MongoDB; consulte ' + str(output))
            processo = subprocess.run(['docker', 'compose', 'exec', '-T', 'mongodb', 'mongosh',
                                      'varejomix_events', '--quiet', '--file', remoto],
                                     cwd=root, capture_output=True)
            saida = (processo.stdout + processo.stderr).decode('utf-8', errors='replace')
            output.write_text(cabecalho + saida, encoding='utf-8')
            validar_saida(saida, processo.returncode)
            return saida
    finally:
        # Limpeza do arquivo temporario; nao altera as colecoes e nao oculta a falha original.
        try:
            subprocess.run(['docker', 'compose', 'exec', '-T', 'mongodb', 'rm', '-f', remoto],
                           cwd=root, capture_output=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            pass
