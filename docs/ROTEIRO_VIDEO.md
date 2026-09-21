# Pitch VarejoMix V2 - até quatro minutos

Os EXPLAIN MongoDB foram confirmados na execução local validada. Use este roteiro como apoio. Apresente com suas palavras e mostre as evidências locais já incluídas. A coleta atual está registrada em 20/09/2026, às 20:39 UTC (20/09/2026, às 17:39 em UTC−3); consulte `evidencias/local/LEIA_ME.md` para identificar as exportações.

## 0:00 a 0:30 - problema e objetivo

Apresente seu nome e a disciplina. Explique que a VarejoMix tem dados de lojas físicas, comércio eletrônico e navegação, e precisa de indicadores confiáveis e uma base de recompra. Informe que os dados usados são sintéticos.

## 0:30 a 1:05 - arquitetura

Mostre a figura do relatório: PostgreSQL para transações, MongoDB para eventos e proposta de lakehouse Parquet/Delta. Explique que o pacote implementa views e exportação CSV/Parquet; a ingestão diária, o Delta e as tabelas dimensionais físicas são evolução proposta.

## 1:05 a 1:45 - integridade e SQL

Mostre `06_validacoes.txt`: zero pedidos antes do cadastro, totais reconciliados e pagamentos coerentes. Explique PK/FK/CHECK, custo histórico do item e regra de venda confirmada. Mostre uma CTE e a janela LAG em `04_queries.sql`.

## 1:45 a 2:15 - índice e plano

Mostre o EXPLAIN local sem e com índice. Compare tipo de acesso, linhas e buffers. Não prometa ganho apenas pelo índice existir nem compare tempos de máquinas diferentes. A consulta seleciona 285 pedidos na carga V2. A evidência atual registra 0,327 ms sem o índice e 0,202 ms com o índice; são tempos de uma única execução.

## 2:15 a 2:45 - NoSQL

Mostre um documento e o funil. Contextos pequenos ficam embutidos; cliente, produto e pedido são referenciados. Há 1.088 eventos, 500 sessões e 78 compras, reconciliadas com os pedidos. A conversão sintética é 15,6%.

## 2:45 a 3:35 - notebook

Mostre `pandas.read_sql`, o corte em 01/10/2025 e a separação das janelas histórica e futura. Apresente o dataset de 162 clientes e 13 colunas: 121 com recompra e 41 sem. Mostre dicionário, ausência de nulos, RFM e exportação.

## 3:35 a 3:55 - reprodutibilidade e conclusão

Mostre `manifesto.json`, o hash e o run_id. Explique que os snapshots são preservados, que a auditoria registra a exportação e que Delta/time travel ainda são proposta. Conclua citando a organização do repositório e das evidências.

## Antes de publicar

Confira áudio, legibilidade e duração. Não mostre tokens do Jupyter. Publique no YouTube (não listado, se preferir) e substitua os links no README e no Word/PDF. Não existe link de vídeo válido enquanto ele não for gravado e publicado.
