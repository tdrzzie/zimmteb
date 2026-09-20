# 0009 — CPU-first evaluation; conservative future 8 GB training

Status: accepted for inference; training design only.

Default to CPU with batch 8 and length 128. `auto` may select CUDA; explicit CUDA
fails clearly when unavailable. An OOM advises smaller batches/length; it never
silently moves requested CUDA execution to CPU.

Future adaptation should use mixed precision, checkpointing, small micro-batches,
cached contrastive loss where justified, checkpoint/resume and separate held-out
evaluation. The planned RTX 4060 training YAML is not executable training code.
Loss choice follows data: in-batch negatives can be false negatives across translated
or equivalent examples. Gradient accumulation is not equivalent to GradCache.
