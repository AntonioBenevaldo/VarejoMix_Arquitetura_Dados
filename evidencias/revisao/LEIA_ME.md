# Evidências da revisão V2

Estas evidências foram produzidas durante a revisão automatizada, usando PostgreSQL embarcado PGlite 18.3. O ambiente previsto para o aluno é PostgreSQL 16 e MongoDB 7 via Docker.

- DDL, carga, views, consultas e validações SQL executados.
- Sete verificações de integridade sem violações; estabilidade da margem histórica verificada em transação com rollback.
- Cinco testes de regressão dos eventos aprovados.
- Reconciliação do JSON com os pedidos PostgreSQL aprovada. A carga JavaScript foi comparada ao JSON com um simulador da interface de inserção; isso não equivale à execução em MongoDB.
- Sete células de código do notebook executadas sequencialmente pelo IPython, com conexão real ao PostgreSQL embarcado. O HTML registra as saídas; um kernel JupyterLab não foi validado neste ambiente.
- Dataset final: 162 clientes, 13 campos, sem nulos ou clientes duplicados; 41 alvos negativos e 121 positivos. Hashes registrados nos manifestos dos snapshots correspondentes em outputs/execucoes/.
- O EXPLAIN documenta os planos observados; uma mudança de plano não comprova ganho de desempenho. Repita as medições no ambiente local.

O arquivo 07_contagens.txt registra o estado anterior às exportações do notebook: pipeline_runs = 0 naquele momento. Três snapshots em outputs/execucoes registram exportações posteriores da revisão PGlite; outros dois documentam a execução local. O manifesto na raiz de outputs aponta a exportação local mais recente. As tabelas de auditoria do banco local começam vazias e serão preenchidas pelas suas próprias execuções.

Na data desta revisão anterior, Docker, MongoDB e JupyterLab ainda aguardavam reprodução local. A coleta local atual foi posteriormente registrada em 20/09/2026, às 19:13 UTC (20/09/2026, às 16:13 em UTC−3); consulte `../local/LEIA_ME.md` e os prints. Os resultados desta pasta continuam sendo os do ambiente de revisão.
