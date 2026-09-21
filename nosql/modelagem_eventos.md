# Modelagem MongoDB - eventos V2

## Grão e contrato

Um documento por evento, com `event_id` único, `schema_version`, `event_time` (BSON Date em UTC), `session_id` e contexto `session`. Tipos: page_view, search, add_to_cart, checkout_start e purchase. A carga contém 1.088 documentos em 500 sessões.

## Embutir versus referenciar

| Critério | Decisão | Justificativa |
|---|---|---|
| Leitura conjunta | Embutir device, page, session e product_context | Contextos pequenos lidos junto ao evento. |
| Cardinalidade | Referenciar customer_id, product_id e order_id | Evita documentos com listas ilimitadas de pedidos/eventos. |
| Atualização | Cadastros permanecem no PostgreSQL | Evita replicar o estado mestre em centenas de documentos. |
| Histórico | Embutir preço exibido e valor observado | Mantém a fotografia do evento. |
| Tamanho | Um evento por documento | Crescimento limitado; não embutir a jornada inteira do cliente. |
| Consistência | PostgreSQL é fonte de verdade das compras | Referências entre bancos exigem validação explícita. |

Referências são identificadores entre sistemas, não FKs que o MongoDB verifica automaticamente. `scripts/validar_eventos.py --mongo` verifica existência do pedido, cliente/canal, valor, quantidade e cronologia, além de comparar o conteúdo do servidor ao JSON entregue.

## Carga e reprodução

`01-mongo-init.js` cria o contrato e os índices, sem inserir exemplos independentes. `02-eventos-sinteticos.js` contém toda a carga coerente. `exemplos_eventos.json` é uma sessão da mesma carga, para leitura.

`data/eventos_sinteticos.json` contém o conjunto completo. O gerador lê vendas digitais confirmadas do PostgreSQL e escolhe 78 com semente fixa; completa 500 sessões com jornadas anônimas sem compra. O funil foi construído para demonstração: 220 sessões com carrinho, 123 com checkout e 78 com compra. Não é um benchmark real.

Datas são normalizadas para milissegundos, compatíveis com BSON Date. Os eventos purchase usam o horário do pagamento (cinco minutos após o pedido na carga). O contexto de origem é consistente ao longo de cada sessão.

## Índices e trade-offs

- `event_id`, único: impede duplicidade, mas uma tentativa repetida de INSERT produz erro; idempotência de ingestão exigiria upsert/deduplicação explícita.
- `session_id, event_time`: recupera a jornada em ordem.
- `customer_id, event_time`: histórico por cliente.
- `event_name, event_time`: filtros por tipo e período.
- `event_time`: filtros temporais.
- Índice parcial de produto: documentos que possuem `product_id`.

Índices custam armazenamento e escrita; sua manutenção deve ser justificada por consultas reais. `03-consultas_funil.js` demonstra agregações e planos. O plano depende do ambiente, e não deve ser forçado para reproduzir uma imagem.

## Limites e governança

MongoDB local é uma instância única, sem demonstração de sharding, failover ou garantia distribuída de disponibilidade. O desenho futuro pode desacoplar telemetria e compra por fila e lotes. TTL só deve ser adotado após preservar os dados necessários na camada histórica. Eventos não substituem pagamento nem estoque transacionais.
