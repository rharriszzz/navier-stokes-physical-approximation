"""Archive the sixth milestone's source benchmark and bounded failure diagnosis."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
import resource

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq
import yaml

from nsblowup.compressed_not_theorem_admissible import CompressedNotTheoremAdmissibleSchedule
from nsblowup.core_not_theorem_admissible import axis_data, radial_operators
from nsblowup.core_representation import source_benchmark, solve_factored, factored_diagnostics, evaluate_fields, SpectralEta, region_norms
from nsblowup.io import ROOT, environment_info, write_summary


LABEL = "Same-tuple representation / NOT theorem-admissible"


def run(config_path, output):
    config = yaml.safe_load(Path(config_path).read_text())
    expected = {"model": "same_tuple_representation_not_theorem_admissible", "datum": "aggressive", "Lambda": 512,
                "g_peak": .1, "sigma_star": .2, "h": .005, "j0": .025, "Y_domain": [0, 4.1], "eta_domain": [-1, 1],
                "lengths": {"intermediate_power": 1, "axial_pulse_swirl_interval": 1, "angular_bump_interval_unbumped": 1, "profile_interpolation": 8, "release_hold": 2}}
    if any(config.get(key) != value for key, value in expected.items()):
        raise ValueError("sixth milestone forbids a changed model tuple")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    start = perf_counter()
    schedule = CompressedNotTheoremAdmissibleSchedule(lengths=config["lengths"])
    benchmark = source_benchmark(schedule, tuple(config["source_counts"]))
    summary = {"label": LABEL, "config": config, "source_benchmark": benchmark, "accepted": False,
               "environment": environment_info(), "cases": [], "plots": [], "next_gate": "C. Improve the local numerical method again"}
    write_summary(output / "source_gate.json", summary)
    if not benchmark["passed"]:
        summary["stopping_reason"] = "source representation did not establish convergence"
        write_summary(output / "summary.json", summary)
        return summary
    count = benchmark["records"][-1]["eta_count"]
    solutions, arrays = [], {}
    for initial in config["initial_guesses"]:
        case_start = perf_counter()
        solution = solve_factored(schedule, config["radial_count_stage_A"], count, initial,
                                  config["iteration_limit"], config["increment_tolerance"])
        best = solution["best_increment_iterate_not_accepted"]
        best_solution = {**solution, **best}
        best_solution["Pbar"] = radial_operators(solution["radial"])[0] @ best["phi"]**2
        record = {"initial": initial, "grid": [solution["radial"].count, count], "status": solution["status"],
                  "history": solution["history"], "best_increment_iteration_not_accepted": best["iteration"], "snapshots": {}}
        for label, snapshot in (("best_increment", best_solution), ("last_retained", solution)):
            diagnostic = factored_diagnostics(schedule, snapshot, 2 * count - 1)
            arrays[initial + "_" + label + "_eta"] = np.array(diagnostic.pop("evaluation_eta"))
            for name, values in diagnostic.pop("residual_eta_slices_at_outer_Y").items():
                arrays[initial + "_" + label + "_residual_" + name] = np.array(values)
            for name, values in diagnostic["modal_slices"].items():
                coefficients = np.array(values.pop("maximum_by_mode"))
                arrays[initial + "_" + label + "_modes_" + name] = coefficients
                values["modal_max_by_twentieth"] = [float(np.max(part)) for part in np.array_split(coefficients, 20)]
            for field in ("phi", "u", "Pbar"):
                arrays[initial + "_" + label + "_" + field] = snapshot[field]
            record["snapshots"][label] = diagnostic
        record["runtime_seconds"] = perf_counter() - case_start
        summary["cases"].append(record)
        solutions.append(solution)
        print(initial, solution["status"], "iterations", len(solution["history"]), "best", best["iteration"],
              "last original residuals", {name: norms["all_eta_linf"] for name, norms in record["snapshots"]["last_retained"]["norms"].items()})
        write_summary(output / "partial_summary.json", summary)
    if all(solution["status"] == "increment_converged_not_accepted" for solution in solutions):
        raise RuntimeError("resolved initial iterations converged; staged refinement must be implemented before any acceptance")
    radius, eta = np.linspace(0, 4.1, 129), SpectralEta(2 * count - 1).nodes[::-1]
    if len(solutions) == 2:
        first, second = [evaluate_fields(solution, radius, len(eta)) for solution in solutions]
        summary["failed_initial_guess_differences_not_branch_evidence"] = {
            name: region_norms((first[name] - second[name]) / (512 if name.startswith("u_") else 1), radius, eta,
                               benchmark["widths"]["eta0"], benchmark["widths"]["g2_standard_deviation_local"])
            for name in first}
    sample = np.linspace(-1, 1, 1001)
    sources = axis_data(schedule, sample)
    intervals = np.flatnonzero(sources["Z"][:-1] * sources["Z"][1:] < 0)
    roots = [brentq(lambda value: float(axis_data(schedule, np.array([value]))["Z"][0]), sample[index], sample[index + 1], xtol=1e-14) for index in intervals]
    root_data = axis_data(schedule, np.array(roots))
    summary["sigma_side_audit_no_solver_change"] = {
        "Z_roots": roots, "Z_root_residuals": root_data["Z"].tolist(),
        "strict_sigma_upper_bounds_at_roots": (np.abs(root_data["H"]) / np.sqrt(99)).tolist(),
        "chi_at_Z_roots_same_sigma": root_data["chi"].tolist(),
        "interpretation": "necessary strict rootwise bounds only, not sufficient for a neighborhood or a theorem condition"}
    figure, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for order, name in enumerate(("G", "G_eta", "G_etaeta")):
        axes[0].loglog([record["eta_count"] for record in benchmark["records"]], [record["relative_linf_G_Geta_Getaeta"][order] for record in benchmark["records"]], "o-", label=name)
    axes[0].set(xlabel="Eta points", ylabel="Source relative Linf error", title="Source-only convergence")
    for record in summary["cases"]:
        axes[1].semilogy([entry["iteration"] for entry in record["history"]], [entry["increment_phi_or_U"] for entry in record["history"]], "o-", label=record["initial"])
    axes[1].set(xlabel="Fixed-point iteration", ylabel="Phi / U increment", title="Resolved iteration fails")
    for axis in axes:
        axis.legend(); axis.grid(alpha=.2)
    figure.suptitle(LABEL)
    figure.savefig(output / "source_and_iteration.png", dpi=150)
    plt.close(figure)
    figure, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for label in ("best_increment", "last_retained"):
        for name in ("angular", "axial"):
            axes[0].semilogy(eta, np.maximum(np.abs(arrays["comparison_" + label + "_residual_" + name]), 1e-16), label=label + " " + name)
        for name in ("phi", "u", "Pbar"):
            values = arrays["comparison_" + label + "_modes_" + name]
            axes[1].semilogy(np.arange(len(values)), np.maximum(values / np.max(values), 1e-18), label=label + " " + name)
    axes[0].set(xlabel="eta", ylabel="Original residual magnitude", title="Y=4.1, endpoints retained")
    axes[1].set(xlabel="Eta mode", ylabel="Normalized modal magnitude", title="Max over Y=.5,2,4.1 slices")
    for axis in axes:
        axis.legend(fontsize=7); axis.grid(alpha=.2)
    figure.suptitle(LABEL + "\nUnaccepted iterates only")
    figure.savefig(output / "residuals_and_modes.png", dpi=150)
    plt.close(figure)
    summary.update({"plots": ["source_and_iteration.png", "residuals_and_modes.png"],
                    "stopping_reason": "source-resolved fixed-point iteration produces nonpositive Phi; no accepted core",
                    "stages": {"A": "stopped at first source-resolved grid; no eta-only solution refinement established",
                               "B": "not run: Stage A failed", "C": "not run: Stages A/B not passed"},
                    "derivative_convergence": "not established; failed-iterate magnitudes and guess differences are not refinement convergence",
                    "B13_comparison": "not recomputed because no numerical acceptance",
                    "completed_utc": datetime.now(timezone.utc).isoformat(), "runtime_seconds": perf_counter() - start,
                    "process_peak_rss_native": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                    "peak_rss_units": "KiB on Linux, bytes on macOS", "no_model_parameter_changed": True})
    arrays.update(Y=solutions[0]["radial"].nodes, eta_nodes=solutions[0]["axial"].nodes)
    np.savez_compressed(output / "unaccepted_arrays.npz", **arrays)
    write_summary(output / "summary.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/core_representation_not_theorem_admissible.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / ("core_representation_not_theorem_admissible_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")))
    arguments = parser.parse_args()
    run(arguments.config, arguments.output)
    print(arguments.output)