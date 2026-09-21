// =====================================================================
// Consultas analíticas sobre a coleção de eventos (MongoDB).
// Uso pelo coletor (arquivo completo via mongosh --file):
//   python scripts/coletar_evidencias.py
//
// Demonstra: agregação, funil de conversão por sessão, série diária,
// ranking de produtos e uso de índice (explain executionStats).
// =====================================================================

db = db.getSiblingDB("varejomix_events");

print("=== 1) Volume por tipo de evento ===");
printjson(
  db.events.aggregate([
    { $group: { _id: "$event_name", eventos: { $sum: 1 },
                sessoes: { $addToSet: "$session_id" } } },
    { $project: { _id: 0, evento: "$_id", eventos: 1,
                  sessoes: { $size: "$sessoes" } } },
    { $sort: { eventos: -1 } }
  ]).toArray()
);

print("=== 2) Funil de conversão por sessão ===");
printjson(
  db.events.aggregate([
    { $group: { _id: "$session_id", etapas: { $addToSet: "$event_name" } } },
    { $group: {
        _id: null,
        sessoes:        { $sum: 1 },
        page_view:      { $sum: { $cond: [{ $in: ["page_view", "$etapas"] }, 1, 0] } },
        add_to_cart:    { $sum: { $cond: [{ $in: ["add_to_cart", "$etapas"] }, 1, 0] } },
        checkout_start: { $sum: { $cond: [{ $in: ["checkout_start", "$etapas"] }, 1, 0] } },
        purchase:       { $sum: { $cond: [{ $in: ["purchase", "$etapas"] }, 1, 0] } }
    } },
    { $project: {
        _id: 0, sessoes: 1, page_view: 1, add_to_cart: 1, checkout_start: 1, purchase: 1,
        taxa_view_para_cart:     { $round: [{ $divide: ["$add_to_cart", "$page_view"] }, 4] },
        taxa_cart_para_checkout: { $round: [{ $divide: ["$checkout_start", "$add_to_cart"] }, 4] },
        taxa_checkout_para_compra: { $round: [{ $divide: ["$purchase", "$checkout_start"] }, 4] },
        conversao_total:         { $round: [{ $divide: ["$purchase", "$page_view"] }, 4] }
    } }
  ]).toArray()
);

print("=== 3) Conversão diária (sessão x dia) ===");
printjson(
  db.events.aggregate([
    { $group: {
        _id: { dia: { $dateToString: { format: "%Y-%m-%d", date: "$event_time" } },
               sessao: "$session_id" },
        etapas: { $addToSet: "$event_name" }
    } },
    { $group: {
        _id: "$_id.dia",
        sessoes:      { $sum: 1 },
        com_carrinho: { $sum: { $cond: [{ $in: ["add_to_cart", "$etapas"] }, 1, 0] } },
        compras:      { $sum: { $cond: [{ $in: ["purchase", "$etapas"] }, 1, 0] } }
    } },
    { $addFields: {
        taxa_conversao: { $round: [{ $divide: ["$compras", "$sessoes"] }, 4] }
    } },
    { $sort: { _id: 1 } }
  ]).toArray()
);

print("=== 4) Top 10 produtos adicionados ao carrinho ===");
printjson(
  db.events.aggregate([
    { $match: { event_name: "add_to_cart" } },
    { $group: {
        _id: { product_id: "$product_id", sku: "$product_context.sku" },
        adicoes: { $sum: 1 },
        preco_medio_exibido: { $avg: "$product_context.displayed_price" }
    } },
    { $project: {
        _id: 0, product_id: "$_id.product_id", sku: "$_id.sku", adicoes: 1,
        preco_medio_exibido: { $round: ["$preco_medio_exibido", 2] }
    } },
    { $sort: { adicoes: -1, sku: 1 } },
    { $limit: 10 }
  ]).toArray()
);

print("=== 5) Origem de tráfego x conversão ===");
printjson(
  db.events.aggregate([
    { $group: {
        _id: { sessao: "$session_id", origem: "$session.source" },
        etapas: { $addToSet: "$event_name" }
    } },
    { $group: {
        _id: "$_id.origem",
        sessoes: { $sum: 1 },
        compras: { $sum: { $cond: [{ $in: ["purchase", "$etapas"] }, 1, 0] } }
    } },
    { $addFields: { conversao: { $round: [{ $divide: ["$compras", "$sessoes"] }, 4] } } },
    { $sort: { conversao: -1 } }
  ]).toArray()
);

print("=== 6) Jornada completa de uma sessão que comprou ===");
var sessaoComCompra = db.events.findOne({ event_name: "purchase" });
printjson(
  db.events.find(
    { session_id: sessaoComCompra.session_id },
    { _id: 0, event_id: 1, event_name: 1, event_time: 1, product_id: 1 }
  ).sort({ event_time: 1 }).toArray()
);

print("=== 7) Uso de índice: explain da consulta por sessão ===");
var plano = db.events.find({ session_id: sessaoComCompra.session_id })
                     .sort({ event_time: 1 })
                     .explain("executionStats");
printjson({
  estagio_vencedor: plano.queryPlanner.winningPlan.inputStage
      ? plano.queryPlanner.winningPlan.inputStage.stage
      : plano.queryPlanner.winningPlan.stage,
  indice: plano.queryPlanner.winningPlan.inputStage
      ? plano.queryPlanner.winningPlan.inputStage.keyPattern
      : null,
  documentos_retornados: plano.executionStats.nReturned,
  documentos_examinados: plano.executionStats.totalDocsExamined,
  chaves_examinadas: plano.executionStats.totalKeysExamined,
  tempo_ms: plano.executionStats.executionTimeMillis
});

print("=== 8) Contraste: consulta sem índice de apoio (COLLSCAN) ===");
var planoSemIndice = db.events.find({ "device.os": "Android" })
                              .explain("executionStats");
printjson({
  estagio: planoSemIndice.queryPlanner.winningPlan.stage,
  documentos_retornados: planoSemIndice.executionStats.nReturned,
  documentos_examinados: planoSemIndice.executionStats.totalDocsExamined,
  tempo_ms: planoSemIndice.executionStats.executionTimeMillis
});

print("=== 9) Índices da coleção ===");
printjson(db.events.getIndexes());
