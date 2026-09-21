db = db.getSiblingDB("varejomix_events");

db.createCollection("events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["event_id", "schema_version", "event_name", "event_time", "session_id", "session"],
      properties: {
        event_id: { bsonType: "string" },
        schema_version: { bsonType: "int", minimum: 1 },
        event_name: {
          enum: ["page_view", "search", "add_to_cart", "checkout_start", "purchase"]
        },
        event_time: { bsonType: "date" },
        session_id: { bsonType: "string" },
        customer_id: { bsonType: ["long", "int", "null"] },
        product_id: { bsonType: ["long", "int", "null"] },
        order_id: { bsonType: ["long", "int", "null"] }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});

db.events.createIndex({ event_id: 1 }, { unique: true });
db.events.createIndex({ event_time: 1 });
db.events.createIndex({ session_id: 1, event_time: 1 });
db.events.createIndex({ customer_id: 1, event_time: -1 });
db.events.createIndex({ event_name: 1, event_time: 1 });
db.events.createIndex(
  { product_id: 1, event_time: 1 },
  { partialFilterExpression: { product_id: { $exists: true } } }
);

