# Correções da revisão V2

1. Corrigido intervalo ativo do cliente para impedir pedidos anteriores ao cadastro.
2. Removida geração de pagamentos recusados para pedidos pagos/enviados/entregues; datas de pagamento coerentes.
3. Centralizada a definição de venda confirmada em `vw_valid_orders`, aplicada a indicadores, cohorts e features.
4. Incluído `unit_cost_at_sale`, com teste que altera o cadastro e confirma estabilidade da margem histórica.
5. Reservas limitadas ao estoque físico no recorte sem backorders.
6. Corrigida a última compra na view de valor do cliente, usando somente vendas confirmadas.
7. Eventos gerados a partir dos pedidos digitais reais; removidos exemplos independentes; datas BSON em milissegundos.
8. Acrescentada reconciliação entre arquivo, MongoDB e PostgreSQL.
9. Removida a amostra offline silenciosa: falhas de conexão interrompem a extração.
10. Corrigidos limites temporais UTC e documentada a história disponível; dicionário completo dos 13 campos.
11. Escores RFM com tratamento igual para empates.
12. Auditoria real de exportação, snapshots por run_id e manifestos com hashes; removidos logs de pipeline simulados.
13. Atualizados o relatório, o README e as contagens. O caso DBEvents foi corrigido para 2019.
14. Identificação do Word original preservada e PDF regenerado a partir dele.
15. Lakehouse/Delta/CDC explicitamente apresentados como evolução; views e arquivos como implementação mínima.
16. Preparação e testes no Windows com lançadores próprios, sem depender da ativação do PowerShell.
17. Pacote sem ambiente virtual, dependências instaladas, caches, notebook vazio ou evidências antigas incompatíveis.

## O que ainda depende do aluno

A execução local e os prints já foram fornecidos e documentados. A correção dos EXPLAIN MongoDB está confirmada em `VALIDACAO_20SET.md`. Falta preencher os links do repositório e do vídeo no README e no Word e exportar novamente o PDF após inserir os links. A finalização documental está descrita em `CORRECOES_FINAIS.md`.
