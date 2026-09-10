import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import yaml


def test_profile_workflow(tmp_path):
    root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((root / "configs/nondimensional.yaml").read_text())
    config["grid"] = [17, 33]
    config["times_to_singularity"] = [1.0, 1e-4]
    config["divergence_grids"] = [[17, 33], [33, 65]]
    config_path = tmp_path / "test.yaml"
    config_path.write_text(yaml.safe_dump(config))
    output = tmp_path / "run"
    subprocess.run([sys.executable, str(root / "scripts/plot_profiles.py"), "--config", str(config_path), "--output", str(output)], check=True, cwd=root)
    summary = json.loads((output / "summary.json").read_text())
    assert len(summary["plots"]) == 7
    assert all((output / filename).stat().st_size > 1000 for filename in summary["plots"])
    np.testing.assert_allclose(summary["slopes_vs_core_radius"]["tangential_max"], -1.01, atol=1e-12)
    assert summary["radial_concentration_factor"] == 100
    assert summary["environment"]["compute_backend"] == "CPU"
    assert summary["environment"]["source_sha256"]
    assert summary["stopping_reason"] == "all configured snapshots evaluated"
    for record in summary["divergence"]["comparison"]:
        assert np.isfinite(record["divergence_linf"])
        if record["observed_order"] is not None:
            assert record["observed_order"] > 1.95


def test_relaxed_pressure_workflow(tmp_path):
    root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((root / "configs/relaxed_not_theorem_admissible.yaml").read_text())
    config["eta_points"] = 65
    config["variations"] = []
    config_path = tmp_path / "relaxed.yaml"
    config_path.write_text(yaml.safe_dump(config))
    output = tmp_path / "relaxed_not_theorem_admissible"
    command = [sys.executable, str(root / "scripts/relaxed_pressure.py"), "--config", str(config_path), "--output", str(output)]
    subprocess.run(command, check=True, cwd=root)
    summary = json.loads((output / "relaxed_not_theorem_admissible_summary.json").read_text())
    assert "NOT theorem-admissible" in summary["label"]
    assert all(summary["records"][0]["validation"]["checks"].values())
    assert len(summary["plots"]) == 3
    assert all((output / filename).stat().st_size > 1000 for filename in summary["plots"])
    assert len(summary["records"][0]["stages"]) == 12
    assert summary["environment"]["source_sha256"]
    assert subprocess.run(command, cwd=root, capture_output=True).returncode != 0