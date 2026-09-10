"""Record the bounded initial B.15 diagnostic, including failed acceptance."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
import os
import resource

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from nsblowup.compressed_not_theorem_admissible import CompressedNotTheoremAdmissibleSchedule
from nsblowup.core_not_theorem_admissible import axis_data, solve_core, independent_residual
from nsblowup.io import ROOT, environment_info, write_summary
from nsblowup.relaxed_schedule import RelaxedSchedule


LABEL = "Unaccepted core iterates / NOT theorem-admissible"


def run(config_path, output):
    config = yaml.safe_load(Path(config_path).read_text())
    if config["model"] != "core_only_not_theorem_admissible" or config["datum"] != "aggressive":
        raise ValueError("this bounded workflow implements the initial aggressive-datum gate only")
    if config["h"] != 0.005 or config["j0"] != 0.025:
        raise ValueError("this milestone fixes h=0.005 and j0=0.025")
    grids = np.asarray(config["grids"])
    if grids.shape != (3, 2) or np.any(grids < 3) or np.any((grids[1:] - 1) % (grids[:-1] - 1)) or np.any(grids[1:] <= grids[:-1]):
        raise ValueError("require three strictly nested increasing Lobatto grids")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = perf_counter()
    schedule = CompressedNotTheoremAdmissibleSchedule(lengths=config["lengths"])
    root = axis_data(schedule, np.array([0.0]), config["Lambda"], config["sigma_star"], config["g_peak"])["eta0"]
    audit_eta = np.unique(np.concatenate((np.linspace(-1, 1, 4097), [root])))
    audit = axis_data(schedule, audit_eta, config["Lambda"], config["sigma_star"], config["g_peak"])
    control = axis_data(RelaxedSchedule(), audit_eta, config["Lambda"], config["sigma_star"], config["g_peak"])
    records, solutions = [], []
    for radial_count, eta_count in config["grids"]:
        case_start = perf_counter()
        solution = solve_core(schedule, radial_count, eta_count, config["Lambda"], config["sigma_star"], config["g_peak"],
                              iterations=config["iteration_limit"], tolerance=config["increment_tolerance"])
        residual = independent_residual(schedule, solution)
        interpolated = solution["axial"].evaluate(audit_eta) @ solution["datum"]["g2"]
        interpolated_derivative = solution["axial"].evaluate(audit_eta, 1) @ solution["datum"]["g2"]
        exact_derivative = 2 * config["Lambda"] * audit["zeta"] * audit["g2"]
        record = {"grid": [radial_count, eta_count], "status": solution["status"], "history": solution["history"],
                  "residual": residual, "runtime_seconds": perf_counter() - case_start,
                  "angular_matrix_condition_max": solution["angular_matrix_condition_max"],
                  "axis_g2_interpolation_linf": float(np.max(np.abs(interpolated - audit["g2"]))),
                  "axis_g2_derivative_linf": float(np.max(np.abs(interpolated_derivative - exact_derivative))),
                  "axis_g2_interpolant_min": float(np.min(interpolated)),
                  "axis_grid_sampled_g_peak": float(np.sqrt(np.max(solution["datum"]["g2"]))),
                  "min_phi_grid": float(np.min(solution["phi"])), "accepted": False}
        records.append(record)
        solutions.append(solution)
        print("GRID", record["grid"], record["status"], "residuals", [norm["linf"] for norm in residual["norms"]],
              "g2 interpolation error", record["axis_g2_interpolation_linf"])
    alternate = solve_core(schedule, *config["grids"][-1], config["Lambda"], config["sigma_star"], config["g_peak"],
                           initial="flat", iterations=config["iteration_limit"], tolerance=config["increment_tolerance"])
    finest = solutions[-1]
    comparison_radius = np.linspace(0, 4.1, 129)
    comparison_eta = np.unique(np.concatenate((np.linspace(-1, 1, 1027), [root])))
    derivative_comparisons = []
    for coarse, fine in zip(solutions[:-1], solutions[1:]):
        differences = {}
        for field, divisor in (("phi", 1), ("u", config["Lambda"]), ("p", config["Lambda"])):
            for radial_order, eta_order, name in ((0, 0, "value"), (1, 0, "Y"), (0, 1, "eta"), (2, 0, "YY"), (0, 2, "etaeta")):
                coarse_values = coarse["radial"].evaluate(comparison_radius, radial_order) @ coarse[field] @ coarse["axial"].evaluate(comparison_eta, eta_order).T / divisor
                fine_values = fine["radial"].evaluate(comparison_radius, radial_order) @ fine[field] @ fine["axial"].evaluate(comparison_eta, eta_order).T / divisor
                differences[field + "_" + name] = float(np.max(np.abs(fine_values - coarse_values)))
        derivative_comparisons.append({"coarse": [coarse["radial"].count, coarse["axial"].count],
                                       "fine": [fine["radial"].count, fine["axial"].count],
                                       "linf_changes": differences})
    initial_guess_check = {"initial": "Phi=1,u=0", "status": alternate["status"], "history": alternate["history"],
                           "phi_difference_from_comparison_initial": float(np.max(np.abs(alternate["phi"] - finest["phi"]))),
                           "U_difference_from_comparison_initial": float(np.max(np.abs(alternate["u"] - finest["u"]))) / config["Lambda"],
                           "interpretation": "same-grid iterate check only, not uniqueness of a converged continuum solution"}
    norms = np.array([[value["linf"] for value in record["residual"]["norms"]] for record in records])
    decreasing = np.all(norms[1:] < norms[:-1], axis=0)
    accepted = bool(np.all(decreasing) and np.all(norms[-1] < config["absolute_residual_gate"]) and
                    all(record["status"] == "increment_converged_not_yet_accepted" and record["residual"]["min_phi_off_grid"] > 0 for record in records))
    if accepted:
        raise RuntimeError("initial gate passed unexpectedly; this failure-recording workflow must not declare a full milestone solution")
    plots = []
    figure, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for index, name in enumerate(("angular", "axial", "pressure")):
        axes[0].loglog([record["grid"][1] for record in records], norms[:, index], "o-", label=name)
    axes[0].set(xlabel="Eta Lobatto nodes", ylabel="Independent B.15 Linf residual")
    for record in records:
        axes[1].semilogy([entry["iteration"] for entry in record["history"]], [entry["increment_phi_or_U"] for entry in record["history"]], label=str(record["grid"]))
    axes[1].set(xlabel="Fixed-point iteration", ylabel="Max Phi / U increment")
    for axis in axes:
        axis.legend(fontsize=8)
        axis.grid(alpha=0.2)
    figure.suptitle(LABEL + "\nSmall increments do not establish equation convergence")
    plots.append("core_not_theorem_admissible_failed_convergence.png")
    figure.savefig(output / plots[-1], dpi=150)
    plt.close(figure)
    figure, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    central = np.abs(audit_eta - root) < 0.04
    axes[0].plot(audit_eta[central], audit["g2"][central], color="black", label="direct axis g^2")
    for solution, record in zip(solutions, records):
        axes[0].plot(audit_eta[central], solution["axial"].evaluate(audit_eta[central]) @ solution["datum"]["g2"], label=str(record["grid"][1]))
    axes[0].set(xlabel="eta", ylabel="g^2", title="Unresolved narrow swirl")
    axes[1].plot(audit_eta, audit["chi"], label="chi")
    axes[1].plot(audit_eta, np.abs(audit["Z"]) / np.max(np.abs(audit["Z"])), label="abs(Z) / max abs(Z)")
    axes[1].axhline(0.99, linestyle=":", color="black", label="chi=0.99")
    axes[1].set(xlabel="eta", title="Finite sigma=0.2 partition audit")
    for axis in axes:
        axis.legend(fontsize=8)
        axis.grid(alpha=0.2)
    figure.suptitle(LABEL)
    plots.append("core_not_theorem_admissible_axis_resolution.png")
    figure.savefig(output / plots[-1], dpi=150)
    plt.close(figure)
    small = np.abs(audit["Z"]) <= 0.1
    small_indices = np.flatnonzero(small)
    small_groups = np.split(small_indices, np.flatnonzero(np.diff(small_indices) > 1) + 1)
    summary = {"label": LABEL, "config": config, "environment": environment_info(), "records": records,
               "completed_utc": datetime.now(timezone.utc).isoformat(),
               "axis_audit": {"eta0": root, "H_range": [float(np.min(audit["H"])), float(np.max(audit["H"]))],
                              "chi_max": float(np.max(audit["chi"])), "chi_above_0p99_count": int(np.sum(audit["chi"] > 0.99)),
                              "small_Z_threshold": 0.1, "small_Z_sample_count": int(np.sum(small)),
                              "small_Z_sampled_intervals": [[float(audit_eta[group[0]]), float(audit_eta[group[-1]])] for group in small_groups if group.size],
                              "chi_range_on_small_Z_samples": [float(np.min(audit["chi"][small])), float(np.max(audit["chi"][small]))] if np.any(small) else None,
                              "Z_at_eta0": float(audit["Z"][np.argmin(np.abs(audit_eta - root))]),
                              "max_abs_Z": float(np.max(np.abs(audit["Z"]))),
                              "log_C": audit["log_C"], "log_g_range": [float(np.min(audit["log_g"])), float(np.max(audit["log_g"]))],
                              "g2_underflow_count": int(np.sum(audit["g2"] == 0)),
                              "control_relative_pressure_difference": float(np.max(np.abs(audit["pressure"] - control["pressure"])) / np.max(np.abs(control["pressure"]))),
                              "control_relative_Z_difference": float(np.max(np.abs(audit["Z"] - control["Z"])) / np.max(np.abs(control["Z"])))},
               "independent_residuals_decrease_each_refinement": decreasing.tolist(),
               "accepted": accepted, "initial_guess_check": initial_guess_check, "plots": plots,
               "unaccepted_derivative_refinement": derivative_comparisons,
               "derivative_comparison_grid": [len(comparison_radius), len(comparison_eta)],
               "derivative_field_units": "phi=Phi, u=U-U_star, p=Pi-Pi0; derivatives in Y and eta",
               "runtime_seconds": perf_counter() - started,
               "process_peak_rss_native": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               "peak_rss_units": "bytes on macOS, KiB on Linux", "openblas_threads": os.environ.get("OPENBLAS_NUM_THREADS", "unspecified"),
               "stopping_reason": "initial Lambda512 g_peak0.1 case fails independent residual refinement; no accepted nonlinear core" if not accepted else "initial gate passed; further continuation requires separate validation",
               "next_gate": "B. Improve the local nonlinear solver first",
               "not_performed": ["Lambda128 or larger g_peak continuation", "nonlinear relaxed control (no accepted aggressive solution)",
                                 "accepted-profile B.17-B.19 continuation diagnostics", "global matching, stress, time integration", "iMac run"],
               "limitations": ["failed iterates are not solutions", "real-axis normalization not theorem C0", "discrete contraction not analytic-norm contraction", "no physical or theorem claim"]}
    write_summary(output / "core_not_theorem_admissible_summary.json", summary)
    np.savez_compressed(output / "core_not_theorem_admissible_unaccepted_iterates.npz",
                        **{f"phi_{index}": solution["phi"] for index, solution in enumerate(solutions)},
                        **{f"u_{index}": solution["u"] for index, solution in enumerate(solutions)},
                        **{f"p_{index}": solution["p"] for index, solution in enumerate(solutions)},
                        **{f"Y_{index}": solution["radial"].nodes for index, solution in enumerate(solutions)},
                        **{f"eta_{index}": solution["axial"].nodes for index, solution in enumerate(solutions)})
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/core_not_theorem_admissible.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / ("core_not_theorem_admissible_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")))
    arguments = parser.parse_args()
    run(arguments.config, arguments.output)
    print(arguments.output)