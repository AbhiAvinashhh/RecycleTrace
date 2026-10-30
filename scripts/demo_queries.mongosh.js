// RecycleTrace - MongoDB Shell (mongosh) Academic Demonstration Script
// Run directly with: mongosh "mongodb://localhost:27017/recycletrace_db" demo_queries.mongosh.js
// Or paste into interactive mongosh shell.

console.log("\n=======================================================");
console.log(" ♻️ RECYCLETRACE - MONGODB SHELL ACADEMIC AUDIT DEMO");
console.log("=======================================================\n");

// 1. View Active Collections
console.log("--- 1. ACTIVE COLLECTIONS ---");
console.log(db.getCollectionNames());

// 2. Inspect $jsonSchema Validation Rules on waste_batches
console.log("\n--- 2. SCHEMA VALIDATION RULES (waste_batches) ---");
const collInfo = db.getCollectionInfos({ name: "waste_batches" })[0];
console.log(JSON.stringify(collInfo.options.validator.$jsonSchema.properties.declared_weight_kg, null, 2));
console.log("Allowed Categories:", collInfo.options.validator.$jsonSchema.properties.waste_category.enum);

// 3. Inspect Created Unique and Compound Indexes
console.log("\n--- 3. INDEXES ON waste_batches ---");
db.waste_batches.getIndexes().forEach(idx => {
  console.log(`- ${idx.name}: ${JSON.stringify(idx.key)} (Unique: ${!!idx.unique})`);
});

// 4. Test Schema Validation Rejection (Negative weight must fail)
console.log("\n--- 4. TESTING $jsonSchema REJECTION (Negative Weight) ---");
try {
  db.waste_batches.insertOne({
    batch_id: "WT-2026-FAIL",
    citizen_id: "demo_user",
    waste_category: "plastic",
    declared_weight_kg: -15.0, // Illegal! Minimum is 0.01
    current_status: "registered",
    created_at: new Date(),
    updated_at: new Date()
  });
  console.log("❌ ERROR: Document should have been rejected!");
} catch (e) {
  console.log("✅ SUCCESS: MongoDB rejected invalid document:");
  console.log("   " + e.message);
}

// 5. Test Unique Index Rejection (Duplicate batch_id)
console.log("\n--- 5. TESTING UNIQUE INDEX REJECTION (Duplicate batch_id) ---");
try {
  db.waste_batches.insertOne({
    batch_id: "WT-2026-1001", // Already exists!
    citizen_id: "demo_user",
    waste_category: "glass",
    declared_weight_kg: 5.0,
    current_status: "registered",
    created_at: new Date(),
    updated_at: new Date()
  });
  console.log("❌ ERROR: Duplicate should have been rejected!");
} catch (e) {
  console.log("✅ SUCCESS: MongoDB rejected duplicate unique index:");
  console.log("   " + e.message);
}

// 6. PIPELINE 1: Status Distribution ($group, $sort)
console.log("\n--- 6. PIPELINE 1: Status Breakdown ($group, $sort) ---");
const p1 = db.waste_batches.aggregate([
  { $group: { _id: "$current_status", count: { $sum: 1 }, total_kg: { $sum: "$declared_weight_kg" } } },
  { $sort: { count: -1 } }
]).toArray();
console.table(p1);

// 7. PIPELINE 2: Facility Throughput ($match, $group, $lookup)
console.log("\n--- 7. PIPELINE 2: Facility Throughput ($lookup, $group) ---");
const p2 = db.processing_records.aggregate([
  {
    $group: {
      _id: "$facility_id",
      reports: { $sum: 1 },
      total_input: { $sum: "$input_weight_kg" },
      verified_recycled: {
        $sum: { $cond: [{ $eq: ["$verification_status", "approved"] }, "$recycled_output_kg", 0] }
      }
    }
  },
  {
    $lookup: {
      from: "facilities",
      localField: "_id",
      foreignField: "facility_id",
      as: "facility"
    }
  },
  { $unwind: "$facility" },
  {
    $project: {
      _id: 0,
      facility_id: "$_id",
      name: "$facility.name",
      reports: 1,
      total_input: { $round: ["$total_input", 2] },
      verified_recycled: { $round: ["$verified_recycled", 2] }
    }
  }
]).toArray();
console.table(p2);

// 8. PIPELINE 3: Daily Collection Trends ($dateTrunc, $group)
console.log("\n--- 8. PIPELINE 3: Daily Trends ($dateTrunc, $group) ---");
const p3 = db.waste_batches.aggregate([
  {
    $group: {
      _id: { $dateTrunc: { date: "$created_at", unit: "day" } },
      batches: { $sum: 1 },
      total_kg: { $sum: "$declared_weight_kg" }
    }
  },
  { $sort: { _id: -1 } },
  {
    $project: {
      _id: 0,
      date: { $dateToString: { format: "%Y-%m-%d", date: "$_id" } },
      batches: 1,
      total_kg: { $round: ["$total_kg", 2] }
    }
  }
]).toArray();
console.table(p3);

// 9. PIPELINE 4: Multi-stage Chain of Custody ($lookup)
console.log("\n--- 9. PIPELINE 4: Integrated Chain of Custody ($lookup) ---");
const p4 = db.waste_batches.aggregate([
  { $match: { current_status: "verified_recycled" } },
  {
    $lookup: {
      from: "facilities",
      localField: "assigned_facility_id",
      foreignField: "facility_id",
      as: "fac"
    }
  },
  { $unwind: { path: "$fac", preserveNullAndEmptyArrays: true } },
  {
    $lookup: {
      from: "processing_records",
      localField: "batch_id",
      foreignField: "batch_id",
      as: "proc"
    }
  },
  { $unwind: { path: "$proc", preserveNullAndEmptyArrays: true } },
  {
    $project: {
      _id: 0,
      batch_id: 1,
      category: "$waste_category",
      facility: "$fac.name",
      input_kg: "$proc.input_weight_kg",
      recycled_kg: "$proc.recycled_output_kg",
      status: "$current_status"
    }
  }
]).toArray();
console.table(p4);

// 10. PIPELINE 5: Executive Multi-Facet ($facet)
console.log("\n--- 10. PIPELINE 5: Multi-Facet Executive Dashboard ($facet) ---");
const p5 = db.waste_batches.aggregate([
  {
    $facet: {
      status_counts: [{ $group: { _id: "$current_status", count: { $sum: 1 } } }],
      categories: [{ $group: { _id: "$waste_category", count: { $sum: 1 } } }],
      total_mass: [{ $group: { _id: null, total_declared_kg: { $sum: "$declared_weight_kg" } } }]
    }
  }
]).toArray();
console.log(JSON.stringify(p5[0], null, 2));

// 11. Live Query Optimization Explain
console.log("\n--- 11. QUERY OPTIMIZATION EXPLAIN (Unique Index on batch_id) ---");
const explain = db.waste_batches.find({ batch_id: "WT-2026-1001" }).explain("executionStats");
console.log("Winning Stage       :", explain.queryPlanner.winningPlan.stage);
console.log("Total Docs Examined :", explain.executionStats.totalDocsExamined);
console.log("Total Keys Examined :", explain.executionStats.totalKeysExamined);
console.log("Execution Time (ms) :", explain.executionStats.executionTimeMillis + " ms");

console.log("\n[✓] Demonstration script execution complete.\n");

