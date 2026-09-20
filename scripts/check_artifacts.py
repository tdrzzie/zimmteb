"""Small tracked-file guard; complements private-key pre-commit checks."""

import re
import subprocess
from pathlib import Path


def main() -> int:
    tracked = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
    errors = []
    patterns = [rb"hf_[A-Za-z0-9]{25,}", rb"gh[pousr]_[A-Za-z0-9]{30,}",
                rb"AKIA[0-9A-Z]{16}", rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"]
    for name in filter(None, tracked):
        path = Path(name)
        if not path.is_file():
            continue
        if path.stat().st_size > 2 * 1024 * 1024:
            errors.append(f"Oversized tracked artifact: {name}")
            continue
        if path.suffix in {".pt", ".bin", ".safetensors"} or path.name == ".env":
            errors.append(f"Disallowed tracked artifact: {name}")
        if any(re.search(pattern, path.read_bytes()) for pattern in patterns):
            errors.append(f"Potential credential in {name} (value not printed)")
    print("\n".join(errors) if errors else "Tracked artifact checks passed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
