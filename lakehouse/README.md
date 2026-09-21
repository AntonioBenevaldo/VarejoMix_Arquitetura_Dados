# Lakehouse: proposta e recorte implementado

## Implementado

O notebook extrai features das views PostgreSQL e grava CSV/Parquet. Cada exportação preserva uma pasta em `outputs/execucoes/<run_id>`, com dicionário e manifesto contendo corte, hashes, versão do código, dimensões e origem. A tabela `audit.pipeline_runs` registra tentativas reais de exportação.

Os snapshots permitem localizar uma versão dos arquivos; não implementam log Delta, MERGE, transações distribuídas, CDC, time travel nem um agendador diário. As views não constituem uma camada OLAP fisicamente isolada.

## Arquitetura futura proposta

- **Bronze:** dados brutos PostgreSQL/MongoDB e metadados `ingestion_ts`, `source_system`, offset, run_id e schema_version.
- **Silver:** normalização de tipos/UTC, deduplicação por chave, validações e quarentena.
- **Gold:** fact_sales no grão item, dimensões de data/cliente/produto/loja/canal, fato de estoque diário, funil e datasets de ML.

Parquet é o formato colunar; Delta Lake acrescentaria log transacional, ACID de tabela, MERGE e consulta de versões. Os componentes precisam ser implementados e testados antes de afirmar que estão operacionais.

## Particionamento e custos

Proposta: ingestion_date e fonte na Bronze; order_date/event_date nas tabelas grandes Silver/Gold. Dimensões pequenas podem ficar sem partições. Evitar particionar por cliente, sessão ou produto devido à alta cardinalidade. Ajustar dia versus mês conforme volume e compactar arquivos pequenos. O dataset de 162 linhas é pequeno e não é particionado.

## Reprocessamento futuro

Registrar período e versões; reler a Bronze; deduplicar; aplicar MERGE; validar totais, chaves, domínio e frescor; publicar somente após aprovação; registrar versão Delta. A política de retenção/VACUUM deve preservar a janela de auditoria e de experimentos acordada. Noventa dias pode ser um ponto de avaliação, não uma regra universal.

## Consistência histórica

A V2 preserva custo histórico nos itens e snapshots de exportação. Reconstruir o estado exato de pedidos, status e categorias em uma data passada exigirá histórico de alterações e/ou versões da fonte. Separar features e alvo por data é necessário, mas não resolve sozinho toda forma de vazamento temporal.
