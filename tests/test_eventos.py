"""Testes de regressao: o validador deve rejeitar erros reais de reconciliacao."""
from pathlib import Path
from unittest.mock import patch
import copy,json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import validar_eventos

class EventValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads((ROOT/'data/eventos_sinteticos.json').read_text(encoding='utf-8'))

    def validate_copy(self,docs):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data').mkdir()
            (root/'data/eventos_sinteticos.json').write_text(json.dumps(docs),encoding='utf-8')
            with patch.object(validar_eventos,'ROOT',root):return validar_eventos.validate()

    def test_valid_fixture(self):
        self.assertEqual(self.validate_copy(self.source)['compras_reconciliadas'],78)

    def test_orphan_purchase_is_rejected(self):
        docs=copy.deepcopy(self.source)
        next(d for d in docs if d['event_name']=='purchase')['order_id']=999999
        with self.assertRaisesRegex(AssertionError,'Pedido inexistente'):self.validate_copy(docs)

    def test_wrong_amount_is_rejected(self):
        docs=copy.deepcopy(self.source)
        next(d for d in docs if d['event_name']=='purchase')['purchase']['total']=0
        with self.assertRaisesRegex(AssertionError,'Valor divergente'):self.validate_copy(docs)

    def test_duplicate_event_is_rejected(self):
        docs=copy.deepcopy(self.source);docs.append(copy.deepcopy(docs[0]))
        with self.assertRaisesRegex(AssertionError,'event_id duplicado'):self.validate_copy(docs)

    def test_event_before_registration_is_rejected(self):
        docs=copy.deepcopy(self.source);docs[0]['event_time']='2020-01-01T00:00:00.000Z'
        with self.assertRaisesRegex(AssertionError,'Evento antes do cadastro'):self.validate_copy(docs)

if __name__=='__main__':unittest.main(verbosity=2)
