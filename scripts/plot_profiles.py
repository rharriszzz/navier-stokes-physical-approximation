"""Plot the sourced Appendix B comparison, not a Navier-Stokes solution."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from nsblowup.coordinates import to_physical, to_similarity
from nsblowup.io import ROOT, environment_info, write_summary
from nsblowup.operators_axisymmetric import divergence
from nsblowup.profiles import ComparisonParameters, comparison_profiles, velocity


def divergence_diagnostics(config, parameters, output):
    records = []
    manufactured_errors = []
    figure, axis = plt.subplots(figsize=(6, 4), constrained_layout=True)
    radial_extent = config["scaled_radial_extent"] / parameters.radial_parameter
    for tau in config["times_to_singularity"]:
        errors = []
        spacings = []
        for radial_count, axial_count in config["divergence_grids"]:
            radius = np.linspace(0, np.sqrt(2 * radial_extent * tau), radial_count)
            _radius, axial_extent, _scale = to_physical(0.0, config["eta_extent"], tau, parameters.h)
            axial = np.linspace(-float(axial_extent), float(axial_extent), axial_count)
            radial_mesh, axial_mesh = np.meshgrid(radius, axial, indexing="ij")
            radial_velocity, _swirl, axial_velocity = velocity(radial_mesh, axial_mesh, tau, parameters)
            defect = divergence(radius, axial, radial_velocity, axial_velocity)
            radial_similarity, eta, scale = to_similarity(radial_mesh, axial_mesh, tau, parameters.h)
            _swirl, _axial, radial_coefficient = comparison_profiles(radial_similarity, eta, parameters)
            gradient_scale = float(np.max(np.abs(radial_coefficient / scale)))
            absolute_error = float(np.max(np.abs(defect)))
            relative_error = absolute_error / gradient_scale
            volume_weight = np.trapezoid(np.trapezoid(radial_mesh, radius, axis=0), axial)
            rms = np.sqrt(np.trapezoid(np.trapezoid(defect**2 * radial_mesh, radius, axis=0), axial) / volume_weight)
            errors.append(relative_error)
            spacings.append(1.0 / (axial_count - 1))
            records.append({
                "tau": float(tau), "grid": [radial_count, axial_count],
                "r_bounds": [0.0, float(radius[-1])], "z_bounds": [float(axial[0]), float(axial[-1])],
                "divergence_linf": absolute_error,
                "divergence_axis_linf": float(np.max(np.abs(defect[0]))),
                "divergence_volume_rms": float(rms), "relative_linf": relative_error,
                "gradient_scale": gradient_scale,
                "observed_order": None if len(errors) == 1 else float(np.log(errors[-2] / errors[-1]) / np.log(spacings[-2] / spacings[-1])),
            })
        axis.loglog(spacings, errors, "o-", label=f"comparison tau={tau:g}")
    for radial_count, axial_count in config["divergence_grids"]:
        radius_test = np.linspace(0, 1, radial_count)
        axial_test = np.linspace(-1, 1, axial_count)
        radial_test, vertical_test = np.meshgrid(radius_test, axial_test, indexing="ij")
        radial_velocity = -radial_test * np.exp(-radial_test**2) * np.cos(vertical_test)
        axial_velocity = 2 * (1 - radial_test**2) * np.exp(-radial_test**2) * np.sin(vertical_test)
        error = float(np.max(np.abs(divergence(radius_test, axial_test, radial_velocity, axial_velocity))))
        manufactured_errors.append({"grid": [radial_count, axial_count], "linf": error})
    axis.loglog([1 / (row["grid"][1] - 1) for row in manufactured_errors],
                [row["linf"] for row in manufactured_errors], "s--", label="manufactured (absolute error)")
    axis.set(xlabel="1 / (N_z - 1)", ylabel="divergence error", title="Second-order physical-grid divergence")
    axis.legend(fontsize=8)
    axis.grid(alpha=0.2)
    figure.savefig(output / "divergence_convergence.png", dpi=150)
    plt.close(figure)
    figure, axis = plt.subplots(figsize=(6, 4), constrained_layout=True)
    image = axis.pcolormesh(radial_mesh, axial_mesh, defect / gradient_scale, shading="auto", cmap="coolwarm")
    figure.colorbar(image, ax=axis, label="divergence / gradient scale")
    axis.set(xlabel="r", ylabel="z", title=f"Comparison divergence, tau={tau:g}, finest grid")
    figure.savefig(output / "divergence_field.png", dpi=150)
    plt.close(figure)
    return {"comparison": records, "manufactured": manufactured_errors,
            "normalization": "Linf(div u) / Linf(V0/(X q)); denominator is the exact radial divergence term",
            "boundary_policy": "all points included; second-order one-sided edges and analytic smooth-axis limit"}


def run(config_path, output):
    config = yaml.safe_load(Path(config_path).read_text())
    parameters = ComparisonParameters(**config["comparison"])
    radial_count, axial_count = config["grid"]
    if min(radial_count, axial_count) < 3:
        raise ValueError("at least three grid points per direction are required")
    radial_extent = float(config["scaled_radial_extent"]) / parameters.radial_parameter
    eta_extent = float(config["eta_extent"])
    if not 0 < radial_extent <= 4.1 / parameters.radial_parameter or not 0 < eta_extent < 1:
        raise ValueError("grid must remain inside the comparison domain")
    times = np.asarray(config["times_to_singularity"], dtype=np.float64)
    if times.ndim != 1 or len(times) < 2 or np.any(~np.isfinite(times)) or np.any(times <= 0) or np.any(np.diff(times) >= 0):
        raise ValueError("provide at least two strictly decreasing positive finite tau values")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    radial_axis = np.linspace(0, radial_extent, radial_count)
    eta_axis = np.linspace(-eta_extent, eta_extent, axial_count)
    radial_mesh, eta_mesh = np.meshgrid(radial_axis, eta_axis, indexing="ij")
    physical_figure, physical_axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    similarity_figure, similarity_axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    field_figure, field_axes = plt.subplots(1, len(times), figsize=(4 * len(times), 4), constrained_layout=True)
    rescaled_figure, rescaled_axes = plt.subplots(1, len(times), figsize=(4 * len(times), 4), constrained_layout=True)
    metrics = []
    for index, tau in enumerate(times):
        radius, axial, scale = to_physical(radial_mesh, eta_mesh, tau, parameters.h)
        radial_velocity, swirl_velocity, axial_velocity = velocity(radius, axial, tau, parameters)
        speed = np.sqrt(radial_velocity**2 + swirl_velocity**2 + axial_velocity**2)
        tangential_speed = np.hypot(swirl_velocity, axial_velocity)
        if not np.all(np.isfinite(speed)):
            raise FloatingPointError("nonfinite comparison velocity")
        jacobian = scale ** (1.5 - parameters.h) * (1 - 2 * parameters.h * eta_mesh**2) / (1 - eta_mesh**2)
        energy = np.pi * np.trapezoid(np.trapezoid(speed**2 * jacobian, radial_axis, axis=0), eta_axis)
        metrics.append({
            "tau": float(tau),
            "r_core": float(np.sqrt(2 * radial_extent * tau)),
            "axial_half_extent": float(np.max(axial)),
            "U_max": float(np.max(speed)),
            "tangential_max": float(np.max(tangential_speed)),
            "swirl_max": float(np.max(np.abs(swirl_velocity))),
            "axial_max": float(np.max(np.abs(axial_velocity))),
            "radial_max": float(np.max(np.abs(radial_velocity))),
            "kinetic_energy_in_window": float(energy),
        })
        mid_radius, mid_axial, mid_scale = to_physical(radial_axis, 0.0, tau, parameters.h)
        mid_radial, mid_swirl, mid_vertical = velocity(mid_radius, mid_axial, tau, parameters)
        physical_values = [mid_radial, mid_swirl, mid_vertical, np.sqrt(mid_radial**2 + mid_swirl**2 + mid_vertical**2)]
        similarity_values = [mid_radial * np.sqrt(mid_scale), mid_swirl * mid_scale ** (0.5 + parameters.h),
                             mid_vertical * mid_scale ** (0.5 + parameters.h),
                             np.hypot(mid_swirl, mid_vertical) * mid_scale ** (0.5 + parameters.h)]
        for axis, values in zip(physical_axes.flat, physical_values):
            axis.plot(mid_radius, values, label=f"tau={tau:g}")
        for axis, values in zip(similarity_axes.flat, similarity_values):
            axis.plot(radial_axis, values, label=f"tau={tau:g}", linestyle=["-", "--", ":", "-."][index % 4])
        image = field_axes[index].contourf(radius, axial, speed, levels=20, cmap="viridis")
        field_figure.colorbar(image, ax=field_axes[index], label="speed")
        field_axes[index].set(xlabel="r", ylabel="z", title=f"tau={tau:g}")
        image = rescaled_axes[index].contourf(radial_mesh, eta_mesh, tangential_speed * scale ** (0.5 + parameters.h), levels=20, cmap="viridis")
        rescaled_figure.colorbar(image, ax=rescaled_axes[index], label="q^A tangential speed")
        rescaled_axes[index].set(xlabel="X", ylabel="eta", title=f"tau={tau:g}")
    for axis, label in zip(physical_axes.flat, ["u_r", "u_theta", "u_z", "speed"]):
        axis.set(xlabel="r at z=0", ylabel=label)
        axis.legend(fontsize=8)
        axis.grid(alpha=0.2)
    for axis, label in zip(similarity_axes.flat, ["q^(1/2) u_r", "q^A u_theta", "q^A u_z", "q^A tangential speed"]):
        axis.set(xlabel="X at eta=0", ylabel=label)
        axis.legend(fontsize=8)
        axis.grid(alpha=0.2)
    plot_files = ["physical_profiles.png", "similarity_profiles.png", "physical_fields.png", "similarity_fields.png"]
    for figure, filename in zip([physical_figure, similarity_figure, field_figure, rescaled_figure], plot_files):
        figure.suptitle("Appendix B explicit comparison (nonlinear core corrections omitted)")
        figure.savefig(output / filename, dpi=150)
        plt.close(figure)
    radii = np.array([row["r_core"] for row in metrics])
    fitted = {name: float(np.polyfit(np.log(radii), np.log([row[name] for row in metrics]), 1)[0])
              for name in ("U_max", "tangential_max", "swirl_max", "axial_max", "radial_max")}
    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for name in ("U_max", "tangential_max", "radial_max"):
        axes[0].loglog(radii, [row[name] for row in metrics], "o-", label=f"{name}: slope {fitted[name]:.5f}")
    axes[0].set(xlabel="prescribed core-window radius", ylabel="maximum velocity")
    axes[0].legend(fontsize=8)
    axes[1].loglog(times, radii, "o-", label="radial window extent")
    axes[1].loglog(times, [row["axial_half_extent"] for row in metrics], "s-", label="axial half extent")
    axes[1].set(xlabel="tau", ylabel="window extent")
    axes[1].legend(fontsize=8)
    figure.suptitle("Prescribed geometry, not dynamically sustained concentration")
    figure.savefig(output / "scaling.png", dpi=150)
    plt.close(figure)
    plot_files.append("scaling.png")
    divergence_results = divergence_diagnostics(config, parameters, output)
    plot_files.extend(["divergence_convergence.png", "divergence_field.png"])
    summary = {
        "environment": environment_info(), "configuration": config,
        "comparison_parameters": asdict(parameters), "precision": "float64",
        "grid_type": "uniform (X, eta), mapped to a curved physical window",
        "time_step_strategy": "none: independent prescribed snapshots",
        "solver_tolerances": {"coordinate_bisections": 56, "axis_quadrature_epsabs": 1e-12, "axis_quadrature_epsrel": 1e-12},
        "r_core_definition": "r at X=Y_max/Lambda, eta=0; prescribed window boundary, not a measured swirl maximum",
        "metrics": metrics, "slopes_vs_core_radius": fitted,
        "divergence": divergence_results,
        "expected_tangential_slope": -1.0 - 2.0 * parameters.h,
        "radial_concentration_factor": float(radii[0] / radii[-1]),
        "velocity_amplification": metrics[-1]["U_max"] / metrics[0]["U_max"],
        "pressure_and_residual": "not evaluated: exterior pressure datum and nonlinear core not constructed",
        "vorticity": "not evaluated in Tasks 1-6",
        "limitations": "Explicit B.13 comparison only; finite parameter hierarchy not certified; no annulus, cutoffs, pulses, or time integration",
        "plots": plot_files, "stopping_reason": "all configured snapshots evaluated",
    }
    write_summary(output / "summary.json", summary)
    print(f"Saved {len(plot_files)} plots and summary to {output}")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/nondimensional.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / datetime.now(timezone.utc).strftime("comparison-%Y%m%dT%H%M%S%fZ"))
    arguments = parser.parse_args()
    run(arguments.config, arguments.output)