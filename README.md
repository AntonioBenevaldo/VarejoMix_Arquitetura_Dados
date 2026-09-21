# VarejoMix - Arquitetura de Dados Híbrida

Projeto da disciplina **Databases for Data Science**, de Ciência de Dados.

- **Aluno:** Antônio Benevaldo Chaves Santana.
- **Professor:** Felipe Becker Nunes.
- **Relatório:** [PDF](relatorio/Relatorio_Tecnico_VarejoMix.pdf) e [Word editável](relatorio/Relatorio_Tecnico_VarejoMix.docx).
- **Repositório:** [https://github.com/AntonioBenevaldo/VarejoMix_Arquitetura_Dados].
- **Vídeo no YouTube, até 4 minutos:** [PREENCHER COM O LINK DO VÍDEO].
- **Comece aqui:** [guia completo](docs/GUIA_DE_TESTE.md) ou abra `docs/guia_de_teste.html` no navegador.

## Situação após a validação final de 20/09/2026

**Parte técnica validada pelas evidências da execução local das 20:39 UTC (17:39 em UTC-3). Pronta para criação do repositório e gravação do vídeo.**

Os 11 testes de regressão passaram. As sete verificações SQL apresentam zero erros e o custo histórico foi aprovado. O log MongoDB registra IXSCAN na consulta por sessão e COLLSCAN na consulta de contraste, sem erros, terminando com VAREJOMIX_MONGO_CONSULTAS_CONCLUIDAS. A falha do coletor anterior está resolvida nesta execução.

Notebook, HTML, CSV, manifesto, snapshot e auditoria identificam a mesma exportação. O hash do código atual confere com o manifesto. A pasta evidencias/local/codigo_da_coleta_20set preserva o código anterior à correção e pertence à execução histórica das 19:13 UTC.

**Falta para a entrega:** criar o repositório acessível ao professor, gravar/publicar o vídeo no YouTube (até quatro minutos), preencher os dois links neste README e no Word e exportar novamente o PDF. Não é necessário repetir os testes para confirmar a correção já demonstrada.

Detalhes: [validação final](docs/VALIDACAO_20SET.md).

## O que foi implementado

| Componente | Implementação |
|---|---|
| PostgreSQL | OLTP normalizado, PK/FK/CHECK, carga determinística, views, CTEs, janelas e EXPLAIN. |
| MongoDB | Contrato JSON Schema, índices, carga de eventos e consultas de funil. |
| Ciência de Dados | SQLAlchemy + pandas.read_sql, features de recompra, RFM e dicionário de 13 campos. |
| Arquivos analíticos | CSV e Parquet; snapshots por execução, hashes e manifesto com corte e versão do código. |
| Auditoria | A tabela começa vazia; o pipeline registra as tentativas de exportação que inicia. |
| Evolução proposta | Ingestão diária agendada, Bronze/Silver/Gold, fatos/dimensões físicos, Delta Lake, MERGE e time travel. |

**Parquet não é Delta Lake.** O recorte implementa exportação colunar e versionamento de arquivos; a arquitetura lakehouse completa permanece proposta no relatório.

## Pré-requisitos

- Windows com Docker Desktop aberto e Docker Compose disponível.
- Python 3.12 ou 3.13 recomendado; dependências em `requirements.txt`. As evidências locais deste pacote registram Python 3.14.6. O ambiente virtual é recriado em cada computador.
- Internet na primeira instalação e pelo menos 4 GB de memória livre.
- Extraia o ZIP inteiro para uma pasta nova, por exemplo `VarejoMix`, na Área de Trabalho. Não execute dentro do ZIP.

O Compose utiliza projeto `varejomix`, portas locais **5434** (PostgreSQL) e **27018** (MongoDB). Isso evita misturar a carga com a instalação anterior. As credenciais são exclusivamente de demonstração local; os serviços ficam vinculados a `127.0.0.1`.

## Execução no Windows - caminho mais simples

1. Abra `01_PREPARAR_WINDOWS.bat` e aguarde `PREPARACAO CONCLUIDA`.
2. Abra `02_TESTAR_WINDOWS.bat`. Ele executa as validações, consultas, EXPLAIN, reconciliação MongoDB e notebook.
3. Ao aparecer **APROVADO**, abra `03_ABRIR_JUPYTERLAB.bat`.
4. No JupyterLab, abra `notebooks/analise_recompra.ipynb` para estudar e apresentar as células. Para repetir: **Run > Run All Cells**; depois salve.
5. Use `04_ENCERRAR_WINDOWS.bat` quando terminar. Os dados persistem.

Os lançadores usam o Python do ambiente virtual diretamente; não exigem ativar PowerShell nem mudar políticas de execução.

## Comandos equivalentes - PowerShell

Abra o terminal dentro da pasta que contém `docker-compose.yml`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
docker compose up -d --wait --wait-timeout 120
.\.venv\Scripts\python.exe scripts\coletar_evidencias.py
.\.venv\Scripts\python.exe -m jupyterlab
```

Se um comando falhar, pare e consulte a mensagem antes de executar o próximo.

## Linux/macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
docker compose up -d --wait --wait-timeout 120
.venv/bin/python scripts/coletar_evidencias.py
.venv/bin/python -m jupyterlab
```

## Ordem técnica

1. O Compose inicializa `01_schema.sql`, `02_seed.sql` e `03_analytics.sql` na primeira criação do volume PostgreSQL.
2. O MongoDB inicializa o contrato e a carga incluída (`01-mongo-init.js`, `02-eventos-sinteticos.js`). Não é necessário executar novamente a geração de eventos.
3. `sql/06_validacoes.sql` verifica cronologia, totais, pagamentos, estoque, grão, receita e custo histórico.
4. `sql/04_queries.sql` demonstra CTE, LAG, média móvel, cohorts e ruptura.
5. `sql/05_index_explain.sql` mede a mesma consulta antes e depois do índice. Tempos não são critérios fixos de aprovação.
6. `validar_eventos.py --mongo` compara o conteúdo MongoDB ao JSON e reconcilia compras com PostgreSQL.
7. `nosql/03-consultas_funil.js` produz funil, rankings e planos MongoDB.
8. O notebook extrai as features, documenta os 13 campos e exporta CSV/Parquet com auditoria.

`sql/08_features.sql` é uma consulta parametrizada pelo Python; não a execute sem fornecer `:cutoff`.

## Regras corrigidas

- Nenhum pedido pode ter data anterior ao cadastro na carga.
- `PAID`, `SHIPPED` e `DELIVERED` possuem pagamento `APPROVED`; `CREATED` é `PENDING`; cancelados são `REFUNDED` no recorte.
- Vendas confirmadas usam a regra central de `analytics.vw_valid_orders`: status confirmado e pagamento aprovado integral.
- Valor líquido significa total dos itens após descontos. Este indicador não é uma apuração fiscal/contábil completa.
- `unit_cost_at_sale` guarda o custo histórico; alterar o produto não muda a margem passada.
- Reservas não excedem estoque físico, pois o recorte não modela backorders.
- Eventos de compra usam pedidos digitais existentes, com cliente, valor, quantidade e data reconciliáveis.

## Resultados

| Indicador | Resultado |
|---|---:|
| Clientes / produtos / lojas | 200 / 40 / 5 |
| Pedidos / itens / pagamentos | 5.000 / 10.068 / 5.000 |
| Snapshots de estoque | 2.800 |
| Vendas confirmadas | 4.730 |
| Valor das vendas confirmadas | R$ 2.688.893,36 |
| Eventos / sessões | 1.088 / 500 |
| Sessões com carrinho / checkout / compra | 220 / 123 / 78 |
| Conversão sessão para compra | 15,6% |
| Dataset final no corte 01/10/2025 UTC | 162 linhas × 13 colunas |
| Alvo de recompra: 0 / 1 | 41 / 121 |
| Nulos / IDs duplicados no dataset | 0 / 0 |

Os números da V1, como 172 clientes e 1.885 eventos, não são mais a referência. O funil é uma distribuição sintética construída para demonstração.

## Evidências da execução validada

A execução local de 20/09/2026, por volta de 20:39 UTC (17:39 em UTC-3), usa PostgreSQL 16.15 e MongoDB 7 no Docker.

| Verificação | Resultado | Evidência |
|---|---|---|
| Serviços | PostgreSQL e MongoDB saudáveis | evidencias/local/docker_compose_ps.txt |
| Integridade | Sete verificações com zero erros; custo histórico aprovado | evidencias/local/06_validacoes.txt |
| Regressão | 11 testes com OK | evidencias/local/testes_regressao.txt |
| Reconciliação | 1.088 eventos, 500 sessões e 78 compras reconciliadas | evidencias/local/eventos_reconciliados.json |
| Planos MongoDB | IXSCAN: 4 documentos e 4 chaves; COLLSCAN: 1.088 documentos | evidencias/local/mongo_local.txt |
| Dataset | 162 clientes × 13 colunas; zero nulos e duplicados | outputs/manifesto.json |
| Demonstração visual atual | Preparação, testes e notebook com o run_id atual | [Word dos prints](relatorio/Testes_Funcionamento_VarejoMix.docx) |

O EXPLAIN PostgreSQL retornou 285 linhas em ambos os planos: Seq Scan em 0,327 ms antes do índice e Bitmap Index Scan + Heap em 0,202 ms depois. São tempos de uma única execução; não constituem benchmark estatístico. As consultas MongoDB 7 e 8 têm filtros diferentes e ilustram tipos de acesso, não uma comparação de desempenho da mesma consulta.

A exportação iniciou em 20/09/2026 às 20:39:24 UTC, com run_id `3dddc761-6614-46a8-be76-bec0129fb04d`. Notebook, HTML, manifesto, snapshot e auditoria correspondem a essa execução. Há cinco registros SUCCESS no banco e doze snapshots preservados. Veja [a identificação das evidências](evidencias/local/LEIA_ME.md).

`evidencias/revisao/` contém a revisão anterior em PGlite/IPython. Os prints sob `evidencias/local/prints/` são históricos; os prints atuais estão em `relatorio/Testes_Funcionamento_VarejoMix.docx`.

## Dataset e reprocessamento

Corte padrão: `2025-10-01T00:00:00Z`. Features: [corte-365 dias, corte). Alvo: [corte, corte+90 dias). A base contém atividade desde dezembro/2024; utiliza-se a história disponível. Clientes sem compra histórica ficam fora do dataset. Status e categorias são do snapshot atual; um caso produtivo exige histórico de mudanças para reconstrução point-in-time.

Cada exportação cria `outputs/execucoes/<run_id>/` com CSV, Parquet, dicionário e manifesto; `outputs/` também recebe os últimos arquivos para acesso rápido. O hash do CSV identifica os dados; o manifesto registra corte, versões e hashes. Reexecutar não insere pedidos ou eventos novamente, nem sobrescreve snapshots anteriores. A auditoria ganha uma execução nova, por isso sua contagem cresce.

A geração opcional `python scripts/gerar_eventos.py` lê a carga PostgreSQL e reescreve os arquivos de eventos; ela não atualiza uma coleção MongoDB já inicializada. Não é necessária para os testes normais da entrega.

## Finalização

A parte técnica está validada e a documentação está sincronizada com a execução das 20:39 UTC. Preencha os links do repositório e do vídeo no início deste README e nos campos amarelos da última página do Word. Depois, salve o Word e exporte novamente `relatorio/Relatorio_Tecnico_VarejoMix.pdf`, mantendo de 6 a 10 páginas. O PDF atual tem 10 páginas. Atualize esses documentos no repositório e no ZIP final. O repositório deve estar acessível ao professor; o vídeo deve estar no YouTube, ter até quatro minutos e pode ser não listado. O roteiro está em `docs/ROTEIRO_VIDEO.md`.

## Conteúdo do ZIP de entrega

Código, carga sintética, diagramas, notebook executado, relatórios, evidências e snapshots. Ambiente virtual, caches, checkpoints e temporários foram retirados. Os arquivos de código e resultados da execução aprovada foram preservados. O relatório técnico, ausente no último ZIP recebido, foi reincluído a partir da revisão anterior e atualizado com os novos resultados. O ambiente pode ser recriado com `01_PREPARAR_WINDOWS.bat`.
