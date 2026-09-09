"""Compact reproducibility metadata for diagnostic runs."""

from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def _command(arguments):
    try:
        return subprocess.check_output(arguments, cwd=ROOT, text=True, stderr=subprocess.STDOUT, timeout=5).strip()
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def environment_info():
    """Record actual runtime hardware and code state; do not assume a GPU."""
    cpu_path = Path("/proc/cpuinfo")
    cpu = next((line.split(":", 1)[1].strip() for line in cpu_path.read_text().splitlines()
                if line.startswith("model name")), "unknown") if cpu_path.exists() else platform.processor()
    memory_path = Path("/proc/meminfo")
    memory = {line.split(":", 1)[0]: line.split(":", 1)[1].strip()
              for line in memory_path.read_text().splitlines()
              if line.startswith(("MemTotal:", "MemAvailable:"))} if memory_path.exists() else {}
    code_files = [ROOT / "pyproject.toml"]
    for directory in ("src", "scripts", "configs", "tests"):
        code_files.extend(path for path in (ROOT / directory).rglob("*")
                          if path.suffix in (".py", ".yaml"))
    return {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.node(),
        "cpu": cpu,
        "memory": memory,
        "gpu": _command(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]),
        "compute_backend": "CPU",
        "packages": dict(sorted((distribution.metadata["Name"], distribution.version)
                                for distribution in metadata.distributions())),
        "git_commit": _command(["git", "rev-parse", "HEAD"]),
        "git_status": _command(["git", "status", "--short"]),
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sorted(code_files)},
    }


def write_summary(path, summary):
    Path(path).write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")