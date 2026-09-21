"""Regressoes do coletor; simulam o processo, sem afirmar execucao MongoDB real."""
from pathlib import Path
from unittest.mock import patch
from subprocess import CompletedProcess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from executar_mongo import executar_consultas_mongo, validar_saida, MARCADOR


class MongoCollectionTests(unittest.TestCase):
    def test_rejects_repl_error_even_with_exit_zero(self):
        with self.assertRaises(RuntimeError):
            validar_saida('Invalid REPL keyword\nUncaught TypeError: winningPlan\n' + MARCADOR, 0)

    def test_rejects_incomplete_output(self):
        with self.assertRaises(RuntimeError):
            validar_saida('=== 7) Uso de indice ===\n', 0)

    def test_rejects_nonzero_exit(self):
        with self.assertRaises(RuntimeError):
            validar_saida(MARCADOR, 1)

    def test_accepts_completed_output(self):
        validar_saida('estagio: COLLSCAN\n' + MARCADOR + '\n', 0)

    def run_mocked(self, returncode, output):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'nosql').mkdir()
            source = 'var p = db.events.find({})\n  .explain("executionStats");'
            (root / 'nosql/03-consultas_funil.js').write_text(source)
            calls = []
            def fake_run(args, **kwargs):
                calls.append(args)
                if args[2] == 'cp':
                    self.assertIn(source, Path(args[3]).read_text())
                    self.assertIn('exit(1)', Path(args[3]).read_text())
                    return CompletedProcess(args, 0, b'', b'')
                if 'mongosh' in args:
                    self.assertIn('--file', args)
                    self.assertNotIn('input', kwargs)
                    return CompletedProcess(args, returncode, output.encode(), b'')
                return CompletedProcess(args, 0, b'', b'')
            destination = root / 'mongo_local.txt'
            with patch('executar_mongo.subprocess.run', side_effect=fake_run):
                if returncode or MARCADOR not in output:
                    with self.assertRaises(RuntimeError):
                        executar_consultas_mongo(root, destination)
                else:
                    executar_consultas_mongo(root, destination)
            self.assertIn(output, destination.read_text())
            self.assertEqual(len(calls), 3)

    def test_executes_whole_file_without_interactive_stdin(self):
        self.run_mocked(0, MARCADOR + '\n')

    def test_preserves_error_log_and_interrupts(self):
        self.run_mocked(1, 'TypeError: falha de demonstracao\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
