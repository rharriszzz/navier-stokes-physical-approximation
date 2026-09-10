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


def test_compressed_workflow(tmp_path):
    root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((root / "configs/compressed_not_theorem_admissible.yaml").read_text())
    config["cases"] = [config["cases"][-1]]
    config_path = tmp_path / "compressed.yaml"
    config_path.write_text(yaml.safe_dump(config))
    output = tmp_path / "compressed_not_theorem_admissible"
    command = [sys.executable, str(root / "scripts/compressed_not_theorem_admissible.py"), "--config", str(config_path), "--output", str(output)]
    subprocess.run(command, check=True, cwd=root)
    summary = json.loads((output / "compressed_not_theorem_admissible_summary.json").read_text())
    baseline, aggressive = summary["records"]
    assert baseline["radius_decades"] > 70
    assert aggressive["radius_decades"] < 10
    assert aggressive["validation"]["explicitly_sacrificed_checks"] == ["interpolation_slope"]
    assert aggressive["conditions"]["conditional_q_matching"]
    assert aggressive["z_relative_change"] < 1e-5
    assert summary["geometry_targets"][-1]["blocked_even_with_zero_adjustable_lengths"]
    assert summary["geometry_targets"][0]["blocked_with_principal_supports_and_eta_slope"]
    assert summary["principal_support_and_eta_slope_radius_decades_lower_bound"] > 30
    assert len(summary["plots"]) == 3
    assert all((output / filename).stat().st_size > 1000 for filename in summary["plots"])
    assert (output / "compressed_not_theorem_admissible_conditions.md").is_file()
    assert subprocess.run(command, cwd=root, capture_output=True).returncode != 0


def test_core_failed_gate_workflow(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "core_not_theorem_admissible"
    command = [sys.executable, str(root / "scripts/core_not_theorem_admissible.py"), "--output", str(output)]
    subprocess.run(command, check=True, cwd=root)
    summary = json.loads((output / "core_not_theorem_admissible_summary.json").read_text())
    assert not summary["accepted"]
    assert summary["independent_residuals_decrease_each_refinement"] == [True, False, False]
    assert summary["axis_audit"]["chi_above_0p99_count"] == 0
    assert summary["next_gate"].startswith("B.")
    assert len(summary["unaccepted_derivative_refinement"]) == 2
    assert len(summary["plots"]) == 2
    assert all((output / filename).stat().st_size > 1000 for filename in summary["plots"])
    assert summary["environment"]["source_sha256"]
    assert summary["records"][-1]["residual"]["norms"][2]["l2_trapezoidal"] > 0
    assert subprocess.run(command, cwd=root, capture_output=True).returncode != 0


def test_same_tuple_representation_failure_workflow(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "same_tuple_not_theorem_admissible"
    command = [sys.executable, str(root / "scripts/core_representation_not_theorem_admissible.py"), "--output", str(output)]
    subprocess.run(command, check=True, cwd=root)
    summary = json.loads((output / "summary.json").read_text())
    assert summary["source_benchmark"]["passed"]
    assert not summary["accepted"]
    assert summary["no_model_parameter_changed"]
    assert summary["next_gate"].startswith("C.")
    assert len(summary["cases"]) == 2
    for case in summary["cases"]:
        assert case["status"] == "phi_nonpositive_proposal"
        assert case["grid"] == [65, 2049]
        norms = case["snapshots"]["best_increment"]["norms"]
        assert norms["pressure"]["all_eta_linf"] < 1e-10
        assert norms["angular"]["eta_endpoints_linf"] > 100 * norms["angular"]["central_source_linf"]
    assert all((output / filename).stat().st_size > 1000 for filename in summary["plots"])
    assert summary["environment"]["source_sha256"]
    assert subprocess.run(command, cwd=root, capture_output=True).returncode != 0
    config = yaml.safe_load((root / "configs/core_representation_not_theorem_admissible.yaml").read_text())
    config["sigma_star"] = 0.1
    config_path = tmp_path / "forbidden.yaml"
    config_path.write_text(yaml.safe_dump(config))
    assert subprocess.run(command + ["--config", str(config_path)], cwd=root, capture_output=True).returncode != 0