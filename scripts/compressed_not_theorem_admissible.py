"""Length-only compression and sacrifice diagnostic; never solves B.15."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from nsblowup.compressed_not_theorem_admissible import CompressedNotTheoremAdmissibleSchedule
from nsblowup.io import ROOT, environment_info, write_summary
from nsblowup.relaxed_schedule import RelaxedParameters, RelaxedSchedule, axial_diagnostic, first_axial_correction
from relaxed_pressure import validate_schedule


LABEL = "Compressed finite model / NOT theorem-admissible"


def run(config_path, output):
    started = perf_counter()
    config = yaml.safe_load(Path(config_path).read_text())
    if config["model"] != "compressed_not_theorem_admissible":
        raise ValueError("explicit modified-model label required")
    reference_config = yaml.safe_load((ROOT / config["reference_config"]).read_text())
    parameters = RelaxedParameters(**reference_config["baseline"])
    baseline = RelaxedSchedule(parameters, reference_config["refined_rtol"], reference_config["refined_atol"])
    reference_lengths = {stage.name: stage.length for stage in baseline.stages}
    eta = np.linspace(-1, 1, reference_config["eta_points"])
    baseline_data = axial_diagnostic(baseline, eta, reference_config["axial_offset"])
    denominator = np.maximum(1, np.max(np.abs(baseline_data["pressure"]), axis=1))
    z_denominator = max(1, float(np.max(np.abs(baseline_data["z_star"]))))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    records, data, schedules = [], {}, {}
    cases = [{"name": "baseline", "group": "reference", "lengths": {}}] + config["cases"]
    for case in cases:
        lengths = {name: reference_lengths[name] * factor for name, factor in case.get("factors", {}).items()}
        if lengths.keys() & case.get("lengths", {}).keys():
            raise ValueError("do not specify both factor and length for the same interval")
        lengths.update(case.get("lengths", {}))
        try:
            schedule = CompressedNotTheoremAdmissibleSchedule(parameters, lengths, reference_config["rtol"], reference_config["atol"])
            tight = CompressedNotTheoremAdmissibleSchedule(parameters, lengths, reference_config["refined_rtol"], reference_config["refined_atol"])
            validation = validate_schedule(schedule, tight, eta, reference_config)
            conditions = schedule.condition_status()
            failed = [name for name, passed in validation["checks"].items() if not passed]
            expected_sacrifices = [] if conditions["eta_slope_bound"] else ["interpolation_slope"]
            if sorted(failed) != expected_sacrifices:
                raise RuntimeError(f"unexpected validation failures: {failed}")
            validation["explicitly_sacrificed_checks"] = expected_sacrifices
            result = axial_diagnostic(tight, eta, reference_config["axial_offset"])
            pressure_change = np.max(np.abs(result["pressure"] - baseline_data["pressure"]), axis=1) / denominator
            z_change = float(np.max(np.abs(result["z_star"] - baseline_data["z_star"])) / z_denominator)
            if max(np.max(pressure_change), z_change) >= 0.1:
                raise RuntimeError("local-data change reaches 0.1; stop for review before further compression")
        except (ValueError, RuntimeError, FloatingPointError) as error:
            write_summary(output / "compressed_not_theorem_admissible_failure.json",
                          {"label": LABEL, "case": case, "error": str(error), "completed_records": records,
                           "environment": environment_info(), "stopping_reason": "construction or numerical validation failed"})
            raise
        correction_records = []
        for radial in config["radial_parameters"]:
            corrected = first_axial_correction(eta, result["z_star"], radial, parameters.h)
            original = first_axial_correction(eta, baseline_data["z_star"], radial, parameters.h)
            correction_records.append({"Lambda": radial, "max_abs_Y4": float(np.max(np.abs(corrected))),
                                       "relative_to_U_star": float(np.max(np.abs(corrected)) / max(1, np.max(np.abs(4 * eta + reference_config["axial_offset"])))),
                                       "max_change_from_baseline": float(np.max(np.abs(corrected - original))),
                                       "root_abs_Y4": float(abs(first_axial_correction(result["eta0"], result["root_z_star"], radial, parameters.h)))})
        record = {"name": case["name"], "group": case["group"], "label": LABEL,
                  "overrides": schedule.overrides, "conditions": conditions, "validation": validation,
                  "log_span": schedule.span, "X_decades": schedule.decades, "radius_decades": schedule.decades / 2,
                  "radius_decades_saved": (baseline.span - schedule.span) / (2 * np.log(10)),
                  "pressure_relative_changes_0_1_2": pressure_change.tolist(), "z_relative_change": z_change,
                  "max_abs_pressure_0_1_2": np.max(np.abs(result["pressure"]), axis=1).tolist(),
                  "max_abs_z": float(np.max(np.abs(result["z_star"]))),
                  "eta0": result["eta0"], "root_pressure_0_1_2": result["root_pressure"].tolist(), "root_z": result["root_z_star"],
                  "corrections": correction_records,
                  "release_XE2_factor": float(np.exp(-2 * next(stage.length for stage in schedule.stages if stage.name == "release_hold"))),
                  "release_E_factor": float(np.exp(-1.5 * next(stage.length for stage in schedule.stages if stage.name == "release_hold"))),
                  "stages": [{"name": stage.name, "start": stage.start, "length": stage.length} for stage in schedule.stages]}
        records.append(record)
        data[case["name"]] = result
        schedules[case["name"]] = tight
        print(f"{case['name']}: radius decades={record['radius_decades']:.6f}; pressure change={pressure_change[0]:.3e}; Z change={z_change:.3e}; Q hold={schedule.q_stop_length:.6f}")
    selected = [record for record in records if record["group"] != "one_at_a_time"]
    plots = []
    figure, axis = plt.subplots(figsize=(12, 6), constrained_layout=True)
    colors = plt.get_cmap("tab20")(np.linspace(0, 1, len(baseline.stages)))
    for position, original_stage in enumerate(baseline.stages):
        axis.barh([record["name"] for record in selected],
                  [record["stages"][position]["length"] / (2 * np.log(10)) for record in selected],
                  left=[record["stages"][position]["start"] / (2 * np.log(10)) for record in selected],
                  color=colors[position], label=original_stage.name.replace("_", " "))
    axis.set(xlabel="Cumulative radius decades (fixed q)", title=LABEL)
    axis.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, fontsize=8)
    plots.append("compressed_not_theorem_admissible_stages.png")
    figure.savefig(output / plots[-1], dpi=150)
    plt.close(figure)
    figure, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    for record in selected:
        name = record["name"]
        axes[0, 0].plot(eta, data[name]["pressure"][0], label=name)
        axes[0, 1].plot(eta, data[name]["z_star"], label=name)
        axes[1, 0].plot(eta, data[name]["pressure"][0] - baseline_data["pressure"][0], label=name)
        axes[1, 1].plot(eta, data[name]["z_star"] - baseline_data["z_star"], label=name)
    for axis, title in zip(axes.flat, ("Pi0", "Z_star", "Pi0 minus baseline", "Z_star minus baseline")):
        axis.set(xlabel="eta", title=title)
        axis.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=8)
    figure.suptitle(LABEL + "\nLocal data only; no nonlinear profile")
    plots.append("compressed_not_theorem_admissible_local_data.png")
    figure.savefig(output / plots[-1], dpi=150)
    plt.close(figure)
    figure, axis = plt.subplots(figsize=(11, 5), constrained_layout=True)
    for record in records[1:]:
        error = max(record["pressure_relative_changes_0_1_2"] + [record["z_relative_change"]])
        combined = record["group"] == "combined"
        axis.scatter(record["radius_decades_saved"], max(error, 1e-14), marker="s" if combined else "o",
                     color="tab:red" if combined else "tab:blue",
                     label="One-at-a-time (cases in condition table)" if record is records[1] else None)
        if combined:
            axis.annotate(record["name"], (record["radius_decades_saved"], max(error, 1e-14)),
                          xytext=(-8, 8), textcoords="offset points", fontsize=9, ha="right")
    axis.set(xlabel="Radius decades saved", ylabel="Max normalized local-data change (display floor 1e-14)", yscale="log", title=LABEL)
    axis.grid(alpha=0.2)
    axis.legend(loc="center left", fontsize=9)
    plots.append("compressed_not_theorem_admissible_tradeoff.png")
    figure.savefig(output / plots[-1], dpi=150)
    plt.close(figure)
    columns = ["reserved_supports_fit", "principal_axial_supports_fit", "principal_angular_supports_fit", "eta_slope_bound", "paper_release_factors", "conditional_q_matching", "global_moments_verified", "stress_verified"]
    table = ["# Compressed finite models: NOT theorem-admissible", "", "Support retention does not establish moment solvability or stress. Q matching is conditional on imposed release data.", "",
             "| Case | Radius decades | " + " | ".join(columns) + " |",
             "| --- | ---: | " + " | ".join(["---"] * len(columns)) + " |"]
    for record in records:
        table.append(f"| {record['name']} | {record['radius_decades']:.6f} | " + " | ".join("yes" if record["conditions"][column] else "no" for column in columns) + " |")
    (output / "compressed_not_theorem_admissible_conditions.md").write_text("\n".join(table) + "\n")
    fixed_floor = (7 + baseline.axial_length) / (2 * np.log(10))
    slope_floor = fixed_floor + 80 * np.log(2) / (2 * np.log(10))
    q_hold_floor = max(0, (np.log(baseline.q_initial / baseline.q_target) - 2) / (1 - parameters.h))
    principal_floor = slope_floor + (11 / parameters.outer_decay + 6.3 + q_hold_floor) / (2 * np.log(10))
    targets = [{"radius_decades": target,
                "evaluated_candidates_reaching_target": [record["name"] for record in selected if record["radius_decades"] <= target],
                "blocked_even_with_zero_adjustable_lengths": bool(target < fixed_floor),
                "blocked_with_eta_slope_bound": bool(target < slope_floor),
                "blocked_with_principal_supports_and_eta_slope": bool(target < principal_floor)} for target in config["targets_radius_decades"]]
    summary = {"label": LABEL, "config": config, "reference_config": reference_config, "parameters": asdict(parameters),
               "environment": environment_info(), "precision": "float64", "eta_points": len(eta), "eta_domain": [-1, 1],
               "records": records, "geometry_targets": targets, "fixed_stage_radius_decades_lower_bound": fixed_floor,
               "eta_slope_retaining_radius_decades_lower_bound": slope_floor,
               "conditional_q_hold_lower_bound": q_hold_floor,
               "principal_support_and_eta_slope_radius_decades_lower_bound": principal_floor, "plots": plots,
               "runtime_seconds": perf_counter() - started,
               "limitations": ["modified A.21-style integral, not unchanged paper datum", "sampled extrema, not certified suprema",
                               "changes below tolerance/roundoff are unresolved, not exact invariance", "conditional Q initial value does not verify global moments",
                               "no B.15, stress, time integration, physical realization or theorem admissibility", "Daisy only; no iMac execution"],
               "stopping_reason": "length-only audit complete; three-radius-decade target blocked by retained early stages; review required before B.15"}
    write_summary(output / "compressed_not_theorem_admissible_summary.json", summary)
    np.savez_compressed(output / "compressed_not_theorem_admissible_profiles.npz", eta=eta,
                        **{name + "_pressure": result["pressure"] for name, result in data.items()},
                        **{name + "_z": result["z_star"] for name, result in data.items()})
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/compressed_not_theorem_admissible.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / ("compressed_not_theorem_admissible_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")))
    arguments = parser.parse_args()
    run(arguments.config, arguments.output)
    print(arguments.output)