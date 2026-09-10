import sys

import numpy as np
import nsblowup


def test_environment():
    assert sys.version_info >= (3, 11)
    assert np.ones(1).dtype == np.float64
    assert nsblowup.__doc__


def test_macos_metadata_branch(monkeypatch):
    from nsblowup import io

    monkeypatch.setattr(io.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(io.platform, "machine", lambda: "arm64")
    responses = {"hw.memsize": str(24 * 1024**3), "machdep.cpu.brand_string": "Apple M4"}
    monkeypatch.setattr(io, "_command", lambda arguments: responses.get(arguments[-1], "unavailable"))
    result = io.environment_info()
    assert result["architecture"] == "arm64"
    assert result["cpu"] == "Apple M4"
    assert result["memory"]["MemTotal"] == "25769803776 bytes"
    assert "unavailable" in result["memory"]["MemAvailable"]
    assert result["compute_backend"] == "CPU"