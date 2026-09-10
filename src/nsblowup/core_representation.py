"""Same-tuple representation diagnostics; NOT theorem-admissible."""

import numpy as np
from numpy.polynomial import chebyshev as cheb
from scipy.fft import dct, idct
from scipy.optimize import minimize_scalar

from nsblowup.core_not_theorem_admissible import axis_data, ChebyshevGrid, radial_operators
from nsblowup.profiles import comparison_function


class SpectralEta:
    """Global Lobatto interpolation using transforms, without dense matrices."""

    def __init__(self, count):
        if not isinstance(count, int) or count < 3:
            raise ValueError("count must be an integer at least three")
        self.count = count
        self.nodes = np.cos(np.pi * np.arange(count) / (count - 1))

    def coefficients(self, values):
        values = np.asarray(values)
        if values.shape[-1] != self.count:
            raise ValueError("last dimension must match the eta grid")
        coefficients = dct(values, type=1, axis=-1) / (self.count - 1)
        coefficients[..., [0, -1]] *= 0.5
        return coefficients

    def differentiate(self, values, order=1):
        coefficients = cheb.chebder(self.coefficients(values), m=order, axis=-1)
        padded = np.zeros_like(values)
        padded[..., :coefficients.shape[-1]] = coefficients
        padded[..., [0, -1]] *= 2
        return idct(padded, type=1, axis=-1) * (self.count - 1)

    def evaluate(self, values, points, order=0):
        coefficients = cheb.chebder(self.coefficients(values), m=order, axis=-1)
        return cheb.chebval(np.asarray(points), np.moveaxis(coefficients, -1, 0))

    def resample(self, values, count, order=0):
        if count < self.count:
            raise ValueError("resampling must not truncate modes")
        coefficients = cheb.chebder(self.coefficients(values), m=order, axis=-1)
        padded = np.zeros((*np.shape(values)[:-1], count))
        padded[..., :coefficients.shape[-1]] = coefficients
        padded[..., [0, -1]] *= 2
        return idct(padded, type=1, axis=-1) * (count - 1)


def exact_source(schedule, eta):
    """Differentiate B.3 analytically at the fixed sixth-milestone tuple."""
    if schedule.parameters.h != 0.005:
        raise ValueError("sixth milestone fixes h=.005")
    eta = np.asarray(eta)
    datum = axis_data(schedule, eta)
    transport_prime = 4.495 - 12 * eta**2 - 0.05 * eta
    denominator_prime = -0.02 * eta
    squared = datum["H"]**2 + 0.2**2
    zeta_prime = (-(denominator_prime * datum["H"] + datum["L"] * transport_prime) / squared
                  + 2 * datum["L"] * datum["H"]**2 * transport_prime / squared**2)
    datum.update({"g": np.exp(datum["log_g"]), "g2_eta": 1024 * datum["zeta"] * datum["g2"],
                  "g2_etaeta": (1024 * zeta_prime + 1024**2 * datum["zeta"]**2) * datum["g2"],
                  "zeta_eta": zeta_prime, "H_eta": transport_prime})
    return datum


def source_widths(schedule):
    root = axis_data(schedule, np.array([0.0]))["eta0"]
    datum = exact_source(schedule, np.array([root]))
    width = 0.2 / np.sqrt(512 * datum["L"][0] * datum["H_eta"][0])
    return {"eta0": root, "g_standard_deviation_local": float(width),
            "g2_standard_deviation_local": float(width / np.sqrt(2)),
            "spacing_513_near_zero": float(np.sin(np.pi / 512)),
            "H_prime_at_eta0": float(datum["H_eta"][0])}


def source_benchmark(schedule, counts=(513, 1025, 2049, 4097)):
    widths = source_widths(schedule)
    root, width = widths["eta0"], widths["g2_standard_deviation_local"]
    reference_eta = np.unique(np.concatenate((np.linspace(-1, 1, 8193), root + np.linspace(-12 * width, 12 * width, 4097), [root])))
    reference = exact_source(schedule, reference_eta)
    records = []
    for count in counts:
        grid = SpectralEta(count)
        datum = exact_source(schedule, grid.nodes)
        interpolated = [grid.evaluate(datum["g2"], reference_eta, order) for order in range(3)]
        exact = [reference[key] for key in ("g2", "g2_eta", "g2_etaeta")]
        errors = [float(np.max(np.abs(actual - expected))) for actual, expected in zip(interpolated, exact)]
        coefficients = grid.coefficients(datum["g2"])
        peak = minimize_scalar(lambda position: -float(grid.evaluate(datum["g2"], position)),
                               bounds=(root - width, root + width), method="bounded", options={"xatol": 1e-15})
        record = {"eta_count": count, "linf_G_Geta_Getaeta": errors,
                  "relative_linf_G_Geta_Getaeta": [error / float(np.max(np.abs(expected))) for error, expected in zip(errors, exact)],
                  "l2_G": float(np.sqrt(np.trapezoid((interpolated[0] - exact[0])**2, reference_eta))),
                  "peak_value_error": abs(float(-peak.fun) - 0.01), "peak_location_error": abs(float(peak.x) - root),
                  "peak_search_success": bool(peak.success), "minimum_interpolated_G": float(np.min(interpolated[0])),
                  "points_across_one_std": int(np.sum(np.abs(grid.nodes - root) <= width / 2)),
                  "points_across_six_std": int(np.sum(np.abs(grid.nodes - root) <= 3 * width)),
                  "modal_tail_ratio": float(np.max(np.abs(coefficients[int(0.9 * count):])) / np.max(np.abs(coefficients))),
                  "modal_max_by_tenth": [float(np.max(np.abs(part))) for part in np.array_split(coefficients, 10)],
                  "source_value_linf": {key: float(np.max(np.abs(grid.evaluate(datum[key], reference_eta) - reference[key])))
                                        for key in ("g", "zeta", "chi", "Z")}}
        record["engineering_gate"] = bool(record["relative_linf_G_Geta_Getaeta"][0] < 1e-4 and record["relative_linf_G_Geta_Getaeta"][1] < 1e-3)
        records.append(record)
        if len(records) >= 3 and record["engineering_gate"] and all(current < previous for current, previous in zip(errors, records[-2]["linf_G_Geta_Getaeta"])):
            break
    return {"widths": widths, "reference_count": len(reference_eta), "records": records,
            "passed": bool(records[-1]["engineering_gate"] and len(records) >= 3 and
                           all(current < previous for current, previous in zip(records[-1]["linf_G_Geta_Getaeta"], records[-2]["linf_G_Geta_Getaeta"]))),
            "point_count_convention": "intervals eta0 +/- std/2 and eta0 +/- 3std; widths are local Gaussian estimates"}


def factored_pressure(phi, phi_eta, phi_etaeta, integral, datum):
    pbar = integral @ phi**2
    pbar_eta = integral @ (2 * phi * phi_eta)
    pbar_etaeta = integral @ (2 * (phi_eta**2 + phi * phi_etaeta))
    return {"Pbar": pbar, "Pbar_eta_integral": pbar_eta, "Pbar_etaeta_integral": pbar_etaeta,
            "p": datum["g2"] * pbar,
            "p_eta": datum["g2_eta"] * pbar + datum["g2"] * pbar_eta,
            "p_etaeta": datum["g2_etaeta"] * pbar + 2 * datum["g2_eta"] * pbar_eta + datum["g2"] * pbar_etaeta}


def solve_factored(schedule, radial_count=65, eta_count=2049, initial="comparison", iterations=80, tolerance=1e-11):
    """Same p148 map, with factored pressure and transform eta derivatives."""
    if initial not in {"comparison", "flat"} or iterations < 1 or not np.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("invalid initial guess or iteration controls")
    radial, axial = ChebyshevGrid(radial_count, 0, 4.1), SpectralEta(eta_count)
    integral, average, inverse_one, inverse_two = radial_operators(radial)
    datum = exact_source(schedule, axial.nodes)
    radius, eta = radial.nodes[:, None], axial.nodes[None, :]
    complement = 1 - eta**2
    phi_zero = comparison_function(radius * datum["chi"])
    correction_zero = -radius * datum["Z"] / (2 * datum["L"])
    phi = phi_zero.copy() if initial == "comparison" else np.ones_like(phi_zero)
    correction = correction_zero.copy() if initial == "comparison" else np.zeros_like(correction_zero)
    angular_inverse = np.linalg.inv(np.eye(radial_count)[None, :, :] + datum["chi"][:, None, None] * inverse_two[None, :, :] / 2)
    history, status = [], "iteration_limit"
    best_increment, best_iterate = np.inf, None
    for iteration in range(iterations):
        velocity = datum["U"] + correction / 512
        average_correction = average @ correction
        transport_w = 1 - 4 * complement - 0.99 * eta * datum["U"] + (-0.99 * eta * average_correction - complement * axial.differentiate(average_correction)) / 512
        transport_h = datum["H"] + complement * correction / 512
        phi_y, phi_eta = radial.derivative @ phi, axial.differentiate(phi)
        correction_y, correction_eta = radial.derivative @ correction, axial.differentiate(correction)
        pbar = integral @ phi**2
        pressure = datum["g2"] * pbar
        pressure_eta = datum["g2_eta"] * pbar + datum["g2"] * (integral @ (2 * phi * phi_eta))
        remainder_one = ((transport_w + .005 * (1 - 2 * eta * velocity) + complement * correction * datum["zeta"]) * phi
                         + transport_w * radius * phi_y + transport_h * phi_eta) / datum["L"]
        remainder_two = (((.505 * (1 - 4 * eta * datum["U"]) + 4 * complement) * correction
                          - 1.01 * eta * correction**2 / 512 + transport_w * radius * correction_y
                          + datum["H"] * correction_eta + complement * correction * correction_eta / 512
                          - 2.02 * eta * pressure + complement * pressure_eta - 2 * eta * radius * datum["g2"] * phi**2) / datum["L"])
        next_phi = phi_zero + np.einsum("eij,je->ie", angular_inverse, inverse_two @ remainder_one) / 1024
        next_correction = correction_zero + inverse_one @ remainder_two / 1024
        increment = max(float(np.max(np.abs(next_phi - phi))), float(np.max(np.abs(next_correction - correction))) / 512)
        if not np.all(np.isfinite(next_phi)) or not np.all(np.isfinite(next_correction)):
            status = "nonfinite_proposal"
            history.append({"iteration": iteration + 1, "nonfinite_proposal": True})
            break
        history.append({"iteration": iteration + 1, "increment_phi_or_U": increment, "min_phi_proposal": float(np.min(next_phi)),
                        "input_rescaled_collocation_linf": [float(np.max(np.abs(value))) for value in (
                            2 * (radius * (radial.derivative @ phi_y) + 2 * phi_y) + datum["chi"] * phi - remainder_one / 512,
                            2 * (radius * (radial.derivative @ correction_y) + correction_y) + datum["Z"] / datum["L"] - remainder_two / 512)]})
        history[-1]["increment_peak_location_Y_eta"] = [float(radial.nodes[index]) if coordinate == 0 else float(axial.nodes[index])
            for coordinate, index in enumerate(np.unravel_index(np.argmax(np.maximum(np.abs(next_phi - phi), np.abs(next_correction - correction) / 512)), phi.shape))]
        history[-1]["eta_modal_tail_ratio"] = {
            name: float(np.max(np.abs(coefficients[..., int(.9 * eta_count):])) / np.max(np.abs(coefficients))) if np.any(coefficients) else 0.0
            for name, values in (("Phi", phi), ("u", correction), ("Pbar", pbar))
            for coefficients in [axial.coefficients(values)]}
        if np.min(next_phi) <= 0 or increment > 10:
            status = "phi_nonpositive_proposal" if np.min(next_phi) <= 0 else "iterate_growth_limit"
            break
        phi, correction = next_phi, next_correction
        if increment < best_increment:
            best_increment = increment
            best_iterate = {"phi": phi.copy(), "u": correction.copy(), "iteration": iteration + 1}
        if increment < tolerance:
            status = "increment_converged_not_accepted"
            break
    return {"phi": phi, "u": correction, "Pbar": integral @ phi**2, "radial": radial, "axial": axial,
            "datum": datum, "history": history, "status": status, "initial": initial,
            "best_increment_iterate_not_accepted": best_iterate,
            "Lambda": 512, "sigma": .2, "peak": .1}


def region_norms(values, radius, eta, root, width):
    absolute = np.abs(values)
    masks = {"all_eta": np.ones_like(eta, dtype=bool), "eta_interior": np.abs(eta) <= .98,
             "central_source": np.abs(eta - root) <= 6 * width, "eta_endpoints": np.abs(eta) == 1}
    norms = {name + "_linf": float(np.max(absolute[:, mask])) for name, mask in masks.items()}
    norms.update({"L2": float(np.sqrt(np.trapezoid(np.trapezoid(values**2, eta, axis=1), radius))),
                  "sampled_RMS": float(np.sqrt(np.mean(values**2))), "axis_linf": float(np.max(absolute[0])),
                  "outer_Y_linf": float(np.max(absolute[-1])), "interior_Y_linf": float(np.max(absolute[1:-1]))})
    location = np.unravel_index(np.argmax(absolute), absolute.shape)
    norms["max_location_Y_eta"] = [float(radius[location[0]]), float(eta[location[1]])]
    return norms


def evaluate_fields(solution, radius, eta_count):
    radial, axial = solution["radial"], solution["axial"]
    fields = {}
    for name in ("phi", "u", "Pbar"):
        for radial_order, eta_order, label in ((0, 0, "value"), (1, 0, "Y"), (2, 0, "YY"), (0, 1, "eta"), (0, 2, "etaeta")):
            fields[name + "_" + label] = axial.resample(radial.evaluate(radius, radial_order) @ solution[name], eta_count, eta_order)[:, ::-1]
    return fields


def factored_diagnostics(schedule, solution, eta_count=4097):
    """Original 4.9 sources and independent derivatives, not R1/R2."""
    radius = np.linspace(0, 4.1, 129)
    eta = SpectralEta(eta_count).nodes[::-1]
    datum, widths = exact_source(schedule, eta), source_widths(schedule)
    fields = evaluate_fields(solution, radius, eta_count)
    phi, correction, pbar = [fields[name + "_value"] for name in ("phi", "u", "Pbar")]
    velocity = datum["U"] + correction / 512
    velocity_y, velocity_yy, velocity_eta = fields["u_Y"] / 512, fields["u_YY"] / 512, 4 + fields["u_eta"] / 512
    pressure = datum["pressure"][0] + datum["g2"] * pbar / 512
    pressure_y = datum["g2"] * fields["Pbar_Y"] / 512
    pressure_eta = datum["pressure"][1] + (datum["g2_eta"] * pbar + datum["g2"] * fields["Pbar_eta"]) / 512
    nodes, weights = np.polynomial.legendre.leggauss(solution["radial"].count + 3)
    average_u = sum(weight / 2 * (solution["radial"].evaluate(radius * (node + 1) / 2) @ solution["u"])
                    for node, weight in zip(nodes, weights))
    averaged = datum["U"] + solution["axial"].resample(average_u, eta_count)[:, ::-1] / 512
    averaged_eta = 4 + solution["axial"].resample(average_u, eta_count, 1)[:, ::-1] / 512
    complement = 1 - eta**2
    transport_w = 1 - .99 * eta * averaged - complement * averaged_eta
    transport_h = .495 * eta + complement * velocity
    with np.errstate(divide="raise", invalid="raise"):
        angular_source = -transport_w * (1 + radius[:, None] * fields["phi_Y"] / phi) - .005 * (1 - 2 * eta * velocity) - transport_h * (512 * datum["zeta"] + fields["phi_eta"] / phi)
        axial_source = (-transport_w * radius[:, None] * velocity_y - .505 * (1 - 2 * eta * velocity) * velocity
                        - transport_h * velocity_eta - complement * pressure_eta + 2.02 * eta * pressure + 2 * eta * radius[:, None] * pressure_y)
        residuals = {"angular": -1024 * datum["L"] * (radius[:, None] * fields["phi_YY"] + 2 * fields["phi_Y"]) / phi - angular_source,
                     "axial": -1024 * datum["L"] * (radius[:, None] * velocity_yy + velocity_y) - axial_source,
                     "pressure": 512 * pressure_y - datum["g2"] * phi**2,
                     "Pbar_radial": fields["Pbar_Y"] - phi**2}
    integral = radial_operators(solution["radial"])[0]
    factored = factored_pressure(solution["phi"], solution["axial"].differentiate(solution["phi"]),
                                solution["axial"].differentiate(solution["phi"], 2), integral, solution["datum"])
    for order, label in ((1, "eta"), (2, "etaeta")):
        identity = solution["axial"].resample(solution["radial"].evaluate(radius) @ factored["Pbar_" + label + "_integral"], eta_count)[:, ::-1]
        residuals["Pbar_" + label + "_identity"] = fields["Pbar_" + label] - identity
    norms = {name: region_norms(value, radius, eta, widths["eta0"], widths["g2_standard_deviation_local"]) for name, value in residuals.items()}
    modes = {}
    for name in ("phi", "u", "Pbar"):
        slices = solution["radial"].evaluate(np.array([.5, 2, 4.1])) @ solution[name]
        coefficients = np.abs(solution["axial"].coefficients(slices))
        modes[name] = {"Y_slices": [.5, 2, 4.1], "tail_ratios": (np.max(coefficients[:, int(.9 * solution["axial"].count):], axis=1) / np.max(coefficients, axis=1)).tolist(),
                       "maximum_by_mode": np.max(coefficients, axis=0).tolist()}
    return {"norms": norms, "modal_slices": modes, "evaluation_shape": [len(radius), len(eta)],
            "min_phi_off_grid": float(np.min(phi)), "accepted": False,
            "source_region_definition": "abs(eta-eta0)<=6 local G standard deviations",
            "derivative_magnitude_by_region": {name: region_norms(value / (512 if name.startswith("u_") else 1), radius, eta, widths["eta0"], widths["g2_standard_deviation_local"])
                                               for name, value in fields.items() if not name.endswith("value")},
            "residual_eta_slices_at_outer_Y": {name: value[-1].tolist() for name, value in residuals.items()}, "evaluation_eta": eta.tolist()}