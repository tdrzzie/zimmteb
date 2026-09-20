# 0006 — Native MTEB results plus a versioned audit envelope

Status: accepted.

Save native MTEB ModelResult JSON and a ZimMTEB `schema_version=1.0` result with
per-query rankings/metrics, model configuration, dataset identity, environment,
timing, resource use and slices. A manifest records running/failed/complete states.
Missing measurements are null, never fabricated zeroes.

Serialize finite numeric values only. Comparisons require identical data versions,
checksums, benchmark version, split and query IDs. JSON is Phase 1's interchange;
Parquet and hosted leaderboard exports wait for stable reviewed data.
