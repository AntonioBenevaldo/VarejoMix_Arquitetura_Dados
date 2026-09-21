# Validação final do VarejoMix

**Parecer técnico: aprovado para seguir com o repositório e o vídeo, com base nos arquivos da execução local de 20/09/2026 às 20:39 UTC (17:39 em UTC-3).**

| Item | Resultado conferido |
|---|---|
| Integridade SQL | Sete verificações com zero erros e custo histórico aprovado. |
| Regressão | 11 testes com OK: 5 de eventos e 6 do controle do coletor. |
| MongoDB | Nove seções concluídas, sem erros; marcador de conclusão presente. |
| Consulta por sessão | IXSCAN, índice session_id/event_time; 4 documentos retornados, 4 examinados e 4 chaves examinadas. |
| Consulta de contraste | COLLSCAN, 1.088 documentos retornados e examinados. |
| Reconciliação | 1.088 eventos, 500 sessões, 78 compras; conversão sintética 15,6%. |
| PostgreSQL EXPLAIN | 285 linhas em ambos os planos; Execution Time 0,327 ms antes e 0,202 ms depois do índice. |
| CSV | 162 linhas × 13 colunas; zero nulos e clientes duplicados; alvo 0: 41 e alvo 1: 121. |
| Dicionário e RFM | Colunas documentadas, somas dos escores e segmentos consistentes. |
| Exportação | Hashes CSV/Parquet conferem com o manifesto; arquivos atuais idênticos ao snapshot. |
| Código | Hash do código atual confere com code_sha256 do manifesto. |
| Notebook | Sete células executadas sem erro salvo; identificador e hash correspondem ao HTML e manifesto. |
| Auditoria | Execução atual registrada como SUCCESS, com 162 linhas; cinco registros no total. |
| Histórico | Doze snapshots preservados; mesmo hash do CSV. |

## Execução identificada

- run_id: 3dddc761-6614-46a8-be76-bec0129fb04d
- Início da exportação: 2026-09-20T20:39:24.176620+00:00
- Hash CSV: c2676febd98e7b65d4dab43dad348bc7bb1c38f3b50b0c2b4bfcf42b4cac2fea
- Hash Parquet: 1faaf84f3ac9d5c4253d064ef0c622518cd6774d6c9e000696ac2839a4fc691e
- Hash código: 520d99141f958ed2626883a5d914edefd0f4cd196352c08d69dc98eeb878ae19

## Correção confirmada

A coleta anterior das 19:13 UTC apresentava falhas nos EXPLAIN MongoDB 7 e 8. A nova execução usa o coletor corrigido com arquivo completo e controle de falhas. O log atual contém os planos e termina com VAREJOMIX_MONGO_CONSULTAS_CONCLUIDAS. A pendência foi encerrada. Não é necessário repetir os testes por causa da atualização documental.

## Conferência com o enunciado

O pacote contém SQL DDL/DML, consultas com CTE/janela/views, índice e EXPLAIN, modelagem NoSQL com justificativas e notebook de extração e features com dicionário, shape, nulos e premissas. O relatório técnico reincluído apresenta arquitetura e diagramas, trade-offs, caso público da Uber e mais de quatro fontes primárias. O PDF tem 10 páginas. Lakehouse completo, Delta e ingestão diária estão descritos como evolução; o recorte prático implementa views e exportação CSV/Parquet.

## Finalização pelo aluno

Criar o repositório com README e os arquivos deste pacote, garantindo acesso ao professor. Gravar e publicar o vídeo no YouTube com até quatro minutos, conforme docs/ROTEIRO_VIDEO.md. Inserir os links no README e Word, exportar o PDF atualizado e incluir os documentos atualizados no repositório e no ZIP final.

## Limites da revisão

A revisão inspecionou os arquivos fornecidos, os logs e os prints da execução local; não executou novamente Docker ou os bancos. O CSV foi lido diretamente. Para Parquet foram conferidos hash e identidade com o snapshot, sem nova leitura tabular. Os tempos SQL são de uma única execução. Os planos MongoDB usam consultas diferentes, portanto não medem ganho de uma mesma consulta antes/depois de índice. Os dados são sintéticos e não representam desempenho em escala de produção.
