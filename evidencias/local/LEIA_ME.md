# Evidências locais validadas

A coleta atual é a de 20/09/2026 às 20:39 UTC (17:39 em UTC-3). SQL, 11 testes, reconciliação, planos MongoDB e exportação estão aprovados nos registros recebidos. A falha MongoDB da execução anterior foi resolvida.

As validações SQL iniciaram às 20:39:11 UTC, o EXPLAIN PostgreSQL às 20:39:12, o MongoDB às 20:39:14, a exportação às 20:39:24 e as contagens às 20:39:28. Os horários são os registrados nos arquivos.

O run_id atual é 3dddc761-6614-46a8-be76-bec0129fb04d. Notebook, HTML, manifesto, snapshot e auditoria correspondem a essa execução. Os hashes do código atual, CSV e Parquet conferem. Consulte ../../docs/VALIDACAO_20SET.md para os resultados e limites da revisão.

## Histórico preservado

| Início UTC | Execução | Origem | Na auditoria atual |
|---|---|---|---|
| 2026-09-05T00:30:52.522390+00:00 | 6e47fc89-725f-48a9-9c00-f671b3ab061c | Revisao automatizada: PostgreSQL embarcado PGlite; Docker e MongoDB devem ser confirmados localmente. | Não |
| 2026-09-05T00:40:13.631293+00:00 | d8b80293-1690-48f1-80d4-2a76db0636e8 | Revisao automatizada: PostgreSQL embarcado PGlite; Docker e MongoDB devem ser confirmados localmente. | Não |
| 2026-09-05T00:41:55.395598+00:00 | 2505c5cd-4e67-41b9-8dcd-90f2aa554af5 | Revisao automatizada: PostgreSQL embarcado PGlite; Docker e MongoDB devem ser confirmados localmente. | Não |
| 2026-09-06T17:15:10.578003+00:00 | 74ca95f7-fca3-4d76-a6d7-049ba87b464e | Execucao local do usuario | Não |
| 2026-09-06T17:21:22.223640+00:00 | ed7ce95f-1568-4b82-b09e-5ca021cd5293 | Execucao local do usuario | Não |
| 2026-09-06T21:05:52.011023+00:00 | a52c83b1-75c5-482a-8ff1-56d2d7c6011d | Execucao local do usuario | Não |
| 2026-09-06T21:08:09.242809+00:00 | 6fd52890-d26d-412c-81cc-61ddd2563820 | Execucao local do usuario | Não |
| 2026-09-06T23:31:38.996619+00:00 | e53b48b9-18c3-4020-87e6-55b78a333cdc | Execucao local do usuario | Sim |
| 2026-09-06T23:34:29.361866+00:00 | 185d5be2-30ba-4c9b-a5cf-1195d19f7ae4 | Execucao local do usuario | Sim |
| 2026-09-07T00:46:21.032530+00:00 | 97a369c3-f9c8-4529-a39f-b76a585323f7 | Execucao local do usuario | Sim |
| 2026-09-20T19:13:33.878017+00:00 | 6809d561-bfd8-4e29-af46-84d21aba7e23 | Execucao local do usuario | Sim |
| 2026-09-20T20:39:24.176620+00:00 | 3dddc761-6614-46a8-be76-bec0129fb04d | Execucao local do usuario | Sim |

Os doze snapshots têm o mesmo hash do CSV. A auditoria retrata o banco na coleta atual; não é um inventário de todos os snapshots acumulados. A ausência de um snapshot histórico nela não demonstra, isoladamente, falha de exportação.

## Código anterior

codigo_da_coleta_20set preserva scripts/sql/nosql anteriores à correção do coletor, relativos à coleta das 19:13 UTC. Seu hash corresponde ao manifesto histórico 6809d561-bfd8-4e29-af46-84d21aba7e23. O manifesto atual corresponde ao código principal corrigido.

## Prints

Os prints atuais estão em ../../relatorio/Testes_Funcionamento_VarejoMix.docx e mostram o run_id atual. O Word em prints/ e as capturas em prints/originais/ são históricos. Os logs e os arquivos exportados são as evidências detalhadas da execução aprovada.
