"""Run the relaxed-hierarchy, NOT theorem-admissible, A.21/B.13 diagnostic."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad
import yaml

from nsblowup.io import ROOT, environment_info, write_summary
from nsblowup.relaxed_schedule import RelaxedParameters, RelaxedSchedule, axial_diagnostic, first_axial_correction, smooth_step


LABEL = "Relaxed hierarchy / NOT theorem-admissible"


def validate_schedule(schedule, refined, eta, config):
    join_errors = np.zeros(3)
    for left, right in zip(schedule.stages[:-1], schedule.stages[1:]):
        for order in range(3):
            join_errors[order] = max(join_errors[order], float(np.max(np.abs(
                left.log_swirl(left.length, eta, order) - right.log_swirl(0, eta, order)))))
    q_checks = []
    for stage, solution in schedule.q_paths:
        def exponent(position):
            return 1.5 * position + float(stage.log_swirl(position, 0) - stage.log_swirl(0, 0))

        source = quad(lambda position: np.exp(exponent(position)) *
                      (-float(stage.log_swirl(position, 0, 1)) - 0.5 - schedule.parameters.h),
                      0, stage.length, epsabs=1e-13, epsrel=1e-12)[0]
        expected = np.exp(-exponent(stage.length)) * (solution.y[0, 0] + source)
        q_checks.append({"stage": stage.name, "initial": float(solution.y[0, 0]),
                         "final": float(solution.y[0, -1]), "integrating_factor_error": float(abs(expected - solution.y[0, -1])),
                         "function_evaluations": solution.nfev})
    values, contributions = schedule.pressure(eta, return_details=True)
    tight_values, tight_contributions = refined.pressure(eta, return_details=True)
    difference = np.max(np.abs(values - tight_values), axis=1)
    relative = difference / np.maximum(1, np.max(np.abs(tight_values), axis=1))
    stage_log_error = max(abs(original["log_integral_eta0"] - tight["log_integral_eta0"])
                          for original, tight in zip(contributions, tight_contributions))
    check_eta = np.linspace(-0.98, 0.98, 97)
    reference = refined.pressure(check_eta)
    differences = []
    for spacing in config["finite_difference_steps"]:
        upper, lower = refined.pressure(check_eta + spacing)[0], refined.pressure(check_eta - spacing)[0]
        approximations = np.stack([(upper - lower) / (2 * spacing), (upper - 2 * reference[0] + lower) / spacing**2])
        errors = np.max(np.abs(approximations - reference[1:]), axis=1)
        orders = None if not differences else (np.log(np.asarray(differences[-1]["absolute_error"]) / errors)
                                                / np.log(differences[-1]["step"] / spacing)).tolist()
        differences.append({"step": spacing, "absolute_error": errors.tolist(),
                            "relative_error": (errors / np.maximum(1, np.max(np.abs(reference[1:]), axis=1))).tolist(),
                            "observed_order": orders})
    interpolation = next(stage for stage in schedule.stages if stage.kind == "interpolation")
    terminal = schedule.stages[-1]
    interpolation_slope = interpolation.log_swirl(np.linspace(0, interpolation.length, 1025)[:, None], eta[None, :], 1) + 0.5
    terminal_ratio = terminal.log_swirl(np.linspace(0, 3, 1025), 0, 1) + 0.5 + schedule.parameters.h
    log_amplitudes = [float(stage.log_swirl(position, axial)) for stage in schedule.stages
                      for position in (0, stage.length / 2, stage.length) for axial in (0, 1)]
    symmetry = float(np.max(np.abs(values[0] - values[0, ::-1])))
    sign_min = float(np.min(eta[eta != 0] * values[1, eta != 0]))
    checks = {
        "joins_logE_first_second_y": bool(np.max(join_errors) < 1e-9),
        "positive_log_swirl_representation": bool(np.all(np.isfinite(log_amplitudes))),
        "positive_ordered_lengths": bool(all(stage.length > 0 for stage in schedule.stages)),
        "infinite_tail_converges": bool(1 + 2 * schedule.parameters.h > 0),
        "q_event": bool(schedule.q_stop_length > 0 and abs(schedule.q_terminal) < 1e-10 and
                        max(record["integrating_factor_error"] for record in q_checks) < 1e-9),
        "pressure_refinement": bool(np.max(relative) < 1e-8 and stage_log_error < 1e-7),
        "derivative_convergence": bool(min(differences[-1]["observed_order"]) > 1.9 and max(differences[-1]["relative_error"]) < 1e-5),
        "pressure_even_and_strict_derivative_sign": bool(symmetry < 1e-10 and sign_min > 0),
        "interpolation_slope": bool(np.min(interpolation_slope) >= -schedule.parameters.outer_decay - 0.1 - 1e-14 and
                                    np.max(interpolation_slope) <= -schedule.parameters.outer_decay + 1e-14),
        "terminal_slope": bool(np.min(terminal_ratio) > -1e-14 and np.max(terminal_ratio) < schedule.parameters.h / 4),
    }
    report = {
        "checks": checks, "join_max_errors": join_errors.tolist(), "q_checks": q_checks,
        "q_initial": schedule.q_initial, "q_before_stopping_hold": schedule.q_before_stop,
        "q_target": schedule.q_target, "q_target_quad_error": schedule.q_target_error,
        "q_stop_length": schedule.q_stop_length, "q_terminal": schedule.q_terminal,
        "span_refinement_difference": abs(schedule.span - refined.span),
        "quadrature_absolute_differences": difference.tolist(), "quadrature_relative_differences": relative.tolist(),
        "max_stage_log_integral_refinement_difference": stage_log_error,
        "derivative_finite_differences": differences, "pressure_evenness_error": symmetry,
        "min_eta_times_pressure_derivative_nonzero_grid": sign_min,
        "interpolation_slope_range": [float(np.min(interpolation_slope)), float(np.max(interpolation_slope))],
        "terminal_log_factor_derivative_range": [float(np.min(terminal_ratio)), float(np.max(terminal_ratio))],
        "finite_stage_sampled_log_amplitude_range": [min(log_amplitudes), max(log_amplitudes)],
        "stage_integrals": contributions,
        "representation": "Log amplitude and log-sum-exp positive moments; tiny contributions retained as logs, tails analytic, no physical radius formed.",
    }
    return report


def requirements(schedule):
    parameters = schedule.parameters
    return {
        "algebraically_satisfied": ["T_d=exp(M_d)+10", "0<h<0.01", "0<h<lambda<1", "P_star>0", "0<j0<=0.05 (checked by axial diagnostic)",
                                     "T_f slope bound", "c_o positivity and slope bound", "convergent infinite ends"],
        "geometrically_satisfied": ["all twelve finite intervals retained and ordered", "four reserved T_w patches fit",
                                    "axial reduction zero for final eleven units", "Q hold reaches Q_p with positive length"],
        "intentionally_relaxed": {
            "P_star>exp(T_d)": {"satisfied": bool(np.log(parameters.pressure_amplitude) > schedule.axial_length),
                                 "log_P_star": float(np.log(parameters.pressure_amplitude)), "required_log_P_star_exceeds": schedule.axial_length},
            "h<exp(-T_d)": {"satisfied": bool(np.log(parameters.h) < -schedule.axial_length),
                             "log_h": float(np.log(parameters.h)), "required_log_h_below": -schedule.axial_length},
            "sufficiently_large_M_d_and_small_lambda_then_h": "not imposed; finite compression authorized",
        },
        "not_checked": ["existence of pressure-preserving angular moment bumps at relaxed parameters", "axial pulse moment closure",
                        "stress cone", "inner/exterior matching", "complex analytic neighborhoods", "sigma_star and C0(Lambda)",
                        "nonlinear B.15 or B.13 asymptotic remainder", "physical dimensionalization"],
    }


def exact_bound_reference():
    from scipy.optimize import brentq

    h, offset = 1e-6, 0.025
    root = brentq(lambda position: (0.5 - h) * position + (1 - position**2) * (4 * position + offset), -0.01, 0, xtol=1e-15)
    axis = 4 * root + offset
    bound = 10 * (0.5 + h) * abs(root) * np.exp(20) / (1 + root**2)**2 - (0.5 + h) * (1 - 2 * root * axis) * axis
    return {"label": "Conditional exact-hierarchy necessary lower bound; NOT an evaluated schedule or nonlinear error",
            "h_illustrative": h, "eta0": root, "z_star_lower_bound": bound,
            "necessary_h_upper_bound": float(np.exp(-10)), "necessary_P_star_lower_bound": float(np.exp(10)),
            "correction_lower_bounds_Y4": {str(radial): 2 * bound / ((1 - 2 * h * root**2) * radial) for radial in (16, 32, 64, 128)}}


def run(config_path, output):
    start = perf_counter()
    config = yaml.safe_load(Path(config_path).read_text())
    if config["model"] != "relaxed_hierarchy_not_theorem_admissible_scheduled_pressure":
        raise ValueError("configuration must explicitly label the relaxed experiment")
    if config["eta_points"] < 33 or config["eta_points"] % 2 != 1:
        raise ValueError("use an odd eta grid with at least 33 points")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    eta = np.linspace(-1, 1, config["eta_points"])
    cases = [{"name": "baseline", "updates": {}}] + config["variations"]
    records, arrays, schedules = [], {}, []
    for case in cases:
        case_start = perf_counter()
        parameters = RelaxedParameters(**(config["baseline"] | case["updates"]))
        schedule = RelaxedSchedule(parameters, config["rtol"], config["atol"])
        refined = RelaxedSchedule(parameters, config["refined_rtol"], config["refined_atol"])
        validation = validate_schedule(schedule, refined, eta, config)
        if not all(validation["checks"].values()):
            write_summary(output / "relaxed_not_theorem_admissible_failure.json", {"label": LABEL, "case": case, "validation": validation})
            raise RuntimeError(f"schedule validation failed for {case['name']}; stop before interpretation")
        diagnostic = axial_diagnostic(refined, eta, config["axial_offset"])
        refined_eta = np.linspace(-1, 1, 2 * config["eta_points"] - 1)
        refined_diagnostic = axial_diagnostic(refined, refined_eta, config["axial_offset"])
        corrections = []
        for radial in config["radial_parameters"]:
            correction = first_axial_correction(eta, diagnostic["z_star"], radial, parameters.h, config["scaled_radius"])
            dense_correction = first_axial_correction(refined_eta, refined_diagnostic["z_star"], radial, parameters.h, config["scaled_radius"])
            corrections.append({"Lambda": radial, "max_abs": float(np.max(np.abs(correction))),
                                "root_abs": float(abs(first_axial_correction(diagnostic["eta0"], diagnostic["root_z_star"], radial, parameters.h, config["scaled_radius"]))),
                                "relative_max": float(np.max(np.abs(correction)) / max(1, np.max(np.abs(4 * eta + config["axial_offset"])))),
                                "eta_grid_refinement_max_difference": float(abs(np.max(np.abs(correction)) - np.max(np.abs(dense_correction))))})
        record = {"name": case["name"], "label": LABEL, "parameters": asdict(parameters), "T_d": schedule.axial_length,
                  "T_w": schedule.power_length, "requirements": requirements(schedule), "log_radial_span": schedule.span,
                  "log10_X_outer_over_X_R": schedule.decades, "validation": validation,
                  "max_abs_pressure_and_derivatives": np.max(np.abs(diagnostic["pressure"]), axis=1).tolist(),
                  "max_abs_z_star": float(np.max(np.abs(diagnostic["z_star"]))),
                  "eta_grid_refinement_z_max_difference": float(abs(np.max(np.abs(diagnostic["z_star"])) - np.max(np.abs(refined_diagnostic["z_star"])))),
                  "eta0": diagnostic["eta0"], "root_iterations": diagnostic["root_iterations"], "root_residual": diagnostic["root_residual"],
                  "root_pressure_and_derivatives": diagnostic["root_pressure"].tolist(), "root_z_star": diagnostic["root_z_star"],
                  "corrections_Y4": corrections, "runtime_seconds": perf_counter() - case_start,
                  "stages": [{"name": stage.name, "start": stage.start, "length": stage.length, "log_start_eta0": stage.log_start,
                              "log_end_eta0": float(stage.log_swirl(stage.length, 0))} for stage in schedule.stages]}
        records.append(record)
        arrays[case["name"] + "_pressure"] = diagnostic["pressure"]
        arrays[case["name"] + "_z_star"] = diagnostic["z_star"]
        schedules.append(schedule)
        print(f"{case['name']}: span={schedule.span:.6f}, decades={schedule.decades:.6f}, max|Pi0|={record['max_abs_pressure_and_derivatives'][0]:.6g}, max|Z|={record['max_abs_z_star']:.6g}")
    plots = []
    figure, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    for record in records:
        for order, axis in enumerate(axes):
            axis.plot(eta, arrays[record["name"] + "_pressure"][order], label=record["name"])
    for axis, title in zip(axes, (r"$\Pi_0$", r"$\Pi_{0\eta}$", r"$\Pi_{0\eta\eta}$")):
        axis.set(xlabel=r"$\eta$", title=title)
        axis.grid(alpha=0.2)
    axes[0].legend(fontsize=8)
    figure.suptitle(LABEL)
    plots.append("relaxed_not_theorem_admissible_pressure.png")
    figure.savefig(output / plots[-1], dpi=150)
    plt.close(figure)
    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for record in records:
        axes[0].plot(eta, arrays[record["name"] + "_z_star"], label=record["name"])
        axes[1].loglog(config["radial_parameters"], [value["max_abs"] for value in record["corrections_Y4"]], "o-", label=record["name"])
    axes[0].set(xlabel=r"$\eta$", ylabel=r"$Z_*$")
    axes[1].set(xlabel=r"$\Lambda$", ylabel=r"$\max|\delta U_1|$ at $Y=4$")
    axes[1].axhline(1, color="black", linestyle=":", linewidth=0.8)
    for axis in axes:
        axis.legend(fontsize=8)
        axis.grid(alpha=0.2)
    figure.suptitle(LABEL + "\nFirst explicit term only; not a nonlinear profile")
    plots.append("relaxed_not_theorem_admissible_correction.png")
    figure.savefig(output / plots[-1], dpi=150)
    plt.close(figure)
    figure, axis = plt.subplots(figsize=(8, 4), constrained_layout=True)
    for record, schedule in zip(records, schedules):
        radius = np.unique(np.concatenate([np.linspace(stage.start, stage.start + stage.length, 101) for stage in schedule.stages]))
        axis.plot(radius / np.log(10), schedule.log_swirl(radius) / np.log(10), label=record["name"])
    axis.set(xlabel=r"$\log_{10}(X/X_R)$", ylabel=r"$\log_{10}E(y,0)$", title=LABEL)
    axis.legend(fontsize=8)
    axis.grid(alpha=0.2)
    plots.append("relaxed_not_theorem_admissible_log_schedule.png")
    figure.savefig(output / plots[-1], dpi=150)
    plt.close(figure)
    np.savez_compressed(output / "relaxed_not_theorem_admissible_profiles.npz", eta=eta, **arrays)
    summary = {"label": LABEL, "config": config, "environment": environment_info(), "float_dtype": "float64",
               "equations": ["A.5-A.13 schedule (pressure-preserving angular bumps omitted)", "A.21", "B.1", "B.12-B.13 first explicit term"],
               "records": records, "exact_hierarchy_bound_reference": exact_bound_reference(), "plots": plots,
               "eta_domain": [-1, 1], "extrema_policy": "sampled grid maxima, doubled eta grid checked; not continuous supremum certificates",
               "runtime_seconds": perf_counter() - start,
               "limitations": ["not theorem-admissible", "unbumped scheduled pressure only; relaxed moment-bump realization unchecked",
                               "no nonlinear solve, momentum residual, time integration or physical dimensionalization", "Daisy execution only; iMac not tested"],
               "stopping_reason": "scheduled-pressure milestone complete; retained radial spans remain physically extreme; review required before B.15"}
    write_summary(output / "relaxed_not_theorem_admissible_summary.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/relaxed_not_theorem_admissible.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / ("relaxed_not_theorem_admissible_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")))
    arguments = parser.parse_args()
    run(arguments.config, arguments.output)
    print(arguments.output)