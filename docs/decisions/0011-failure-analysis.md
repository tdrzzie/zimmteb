# 0011 — Mechanical failure labels before semantic diagnoses

Status: accepted.

Retain rankings and per-query relevance metrics. Flag wrong first results, missing
top-10 positives and hard negatives in top-5; preserve language/domain/code-switch
context. Never automatically label an error a lexical trap or translation failure
without review. Those are future reviewer annotations.

Paired query bootstrap is available for matched runs. Correlated paraphrases and tiny
synthetic samples invalidate strong inferential conclusions; future evaluation needs
cluster-aware resampling and sufficient independent source units.
