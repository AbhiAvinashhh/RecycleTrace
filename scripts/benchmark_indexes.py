"""
RecycleTrace - MongoDB Index Optimization Benchmark
Reproducible before-and-after indexing benchmark on synthetic dataset using explain("executionStats").
No fabricated numbers — reports exact MongoDB query planner statistics.
"""
import sys
import os
import time
from datetime import datetime, timezone
from pymongo import MongoClient, ASCENDING

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import get_config

def run_reproducible_benchmark():
    cfg = get_config()
    client = MongoClient(cfg.MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.get_default_database()

    bench_coll = db["benchmark_batches"]
    bench_coll.drop() # clean start

    TOTAL_RECORDS = 10000
    print(f"[*] Generating {TOTAL_RECORDS} synthetic waste batches for indexing benchmark...")

    now = datetime.now(timezone.utc)
    categories = ["plastic", "paper", "glass", "metal", "organic", "e-waste"]
    statuses = ["registered", "collected", "in_transit", "received", "processing", "verified_recycled"]

    docs = []
    for i in range(1, TOTAL_RECORDS + 1):
        docs.append({
            "batch_id": f"BENCH-WT-2026-{i:05d}",
            "citizen_id": f"CITIZEN_{i % 250:03d}",
            "waste_category": categories[i % len(categories)],
            "current_status": statuses[i % len(statuses)],
            "declared_weight_kg": round(5.0 + (i % 45) * 1.2, 2),
            "created_at": now
        })
    bench_coll.insert_many(docs)
    print(f"[*] {TOTAL_RECORDS} documents inserted.")

    target_batch = "BENCH-WT-2026-07500"
    target_citizen = "CITIZEN_042"
    target_status = "registered"

    print("\n" + "="*70)
    print(" BENCHMARK TEST 1: Single Field Lookup by batch_id")
    print(" Query: {'batch_id': '" + target_batch + "'}")
    print("="*70)

    # 1A. BEFORE INDEX (Collection Scan)
    explain_before = bench_coll.find({"batch_id": target_batch}).explain()
    stats_before = explain_before["executionStats"]
    planner_before = explain_before["queryPlanner"]

    print("\n--- [A] BEFORE INDEX (No Index on batch_id) ---")
    print(f" Winning Stage       : {planner_before['winningPlan']['stage']}")
    print(f" Total Docs Examined : {stats_before['totalDocsExamined']}")
    print(f" Total Keys Examined : {stats_before['totalKeysExamined']}")
    print(f" Execution Time (ms) : {stats_before['executionTimeMillis']} ms")
    print(f" Documents Returned  : {stats_before['nReturned']}")

    # 1B. APPLY INDEX
    print("\n[*] Creating Unique Index on 'batch_id'...")
    t0 = time.time()
    bench_coll.create_index([("batch_id", ASCENDING)], unique=True, name="idx_bench_batch_id")
    index_time = (time.time() - t0) * 1000
    print(f"[*] Index created in {index_time:.2f} ms.")

    # 1C. AFTER INDEX (Index Scan)
    explain_after = bench_coll.find({"batch_id": target_batch}).explain()
    stats_after = explain_after["executionStats"]
    planner_after = explain_after["queryPlanner"]

    # In MongoDB, winningPlan could be FETCH with inputStage IXSCAN
    winning_stage = planner_after['winningPlan']['stage']
    input_stage = planner_after['winningPlan'].get('inputStage', {}).get('stage', 'N/A')

    print("\n--- [B] AFTER INDEX (Unique Index on batch_id) ---")
    print(f" Winning Stage       : {winning_stage} -> {input_stage}")
    print(f" Total Docs Examined : {stats_after['totalDocsExamined']}")
    print(f" Total Keys Examined : {stats_after['totalKeysExamined']}")
    print(f" Execution Time (ms) : {stats_after['executionTimeMillis']} ms")
    print(f" Documents Returned  : {stats_after['nReturned']}")

    print("\n" + "="*70)
    print(" BENCHMARK TEST 2: Compound Query (citizen_id + current_status)")
    print(f" Query: {{'citizen_id': '{target_citizen}', 'current_status': '{target_status}'}}")
    print("="*70)

    # 2A. BEFORE COMPOUND INDEX
    explain_comp_before = bench_coll.find({"citizen_id": target_citizen, "current_status": target_status}).explain()
    c_stats_before = explain_comp_before["executionStats"]
    c_plan_before = explain_comp_before["queryPlanner"]

    print("\n--- [A] BEFORE COMPOUND INDEX ---")
    print(f" Winning Stage       : {c_plan_before['winningPlan']['stage']}")
    print(f" Total Docs Examined : {c_stats_before['totalDocsExamined']}")
    print(f" Total Keys Examined : {c_stats_before['totalKeysExamined']}")
    print(f" Execution Time (ms) : {c_stats_before['executionTimeMillis']} ms")

    # 2B. CREATE COMPOUND INDEX
    print("\n[*] Creating Compound Index [('citizen_id', 1), ('current_status', 1)]...")
    bench_coll.create_index([("citizen_id", ASCENDING), ("current_status", ASCENDING)], name="idx_bench_citizen_status")

    # 2C. AFTER COMPOUND INDEX
    explain_comp_after = bench_coll.find({"citizen_id": target_citizen, "current_status": target_status}).explain()
    c_stats_after = explain_comp_after["executionStats"]
    c_plan_after = explain_comp_after["queryPlanner"]

    c_win_stage = c_plan_after['winningPlan']['stage']
    c_inp_stage = c_plan_after['winningPlan'].get('inputStage', {}).get('stage', 'N/A')

    print("\n--- [B] AFTER COMPOUND INDEX ---")
    print(f" Winning Stage       : {c_win_stage} -> {c_inp_stage}")
    print(f" Total Docs Examined : {c_stats_after['totalDocsExamined']}")
    print(f" Total Keys Examined : {c_stats_after['totalKeysExamined']}")
    print(f" Execution Time (ms) : {c_stats_after['executionTimeMillis']} ms")

    print("\n" + "="*70)
    print(" BENCHMARK AUDIT SUMMARY (ACADEMIC REPORT)")
    print("="*70)
    print(f"Lookup Test: Scanned docs reduced from {stats_before['totalDocsExamined']} to {stats_after['totalDocsExamined']} (COLLSCAN -> IXSCAN).")
    print(f"Compound Test: Scanned docs reduced from {c_stats_before['totalDocsExamined']} to {c_stats_after['totalDocsExamined']} (COLLSCAN -> IXSCAN).")
    print("All measurements were produced by live MongoDB explain('executionStats').")

    # Clean up benchmark collection
    bench_coll.drop()
    print("[*] Benchmark collection cleaned up.")

if __name__ == "__main__":
    run_reproducible_benchmark()
