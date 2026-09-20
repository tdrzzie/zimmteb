import importlib.metadata
import platform
import subprocess
import threading
from typing import Any

import psutil


def system_info() -> dict[str, Any]:
    import torch

    versions = {}
    for package in ("zimmteb", "mteb", "sentence-transformers", "transformers", "datasets", "torch", "numpy", "huggingface-hub"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "unavailable"
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True))
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    return {"python": platform.python_version(), "os": platform.platform(),
            "cpu": platform.processor() or platform.machine(), "cpu_count": psutil.cpu_count(),
            "ram_bytes": psutil.virtual_memory().total, "packages": versions,
            "cuda_available": torch.cuda.is_available(), "cuda_version": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "git_commit": commit, "git_dirty": dirty}


def select_device(requested: str) -> str:
    import torch

    if requested not in {"auto", "cpu", "cuda"}:
        raise ValueError("Device must be auto, cpu or cuda")
    if requested == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if requested == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA requested but unavailable. Install a compatible CUDA PyTorch build or select --device cpu.")
    return requested


class MemorySampler:
    """Approximate process RSS peak sampled every 20 ms, not total system RAM."""

    def __init__(self) -> None:
        self.peak = psutil.Process().memory_info().rss
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._sample, daemon=True)

    def _sample(self) -> None:
        process = psutil.Process()
        while not self.stop.wait(0.02):
            self.peak = max(self.peak, process.memory_info().rss)

    def __enter__(self) -> "MemorySampler":
        self.thread.start()
        return self

    def __exit__(self, *args: Any) -> None:
        self.stop.set()
        self.thread.join()
