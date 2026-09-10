"""Experimental B.15 radial-inverse solver, NOT theorem-admissible."""

import numpy as np
from numpy.polynomial import chebyshev as cheb
from numpy.polynomial.legendre import leggauss
from scipy.fft import dct
from scipy.integrate import quad
from scipy.optimize import brentq

from nsblowup.profiles import comparison_function


class ChebyshevGrid:
    def __init__(self, count, lower, upper):
        if not isinstance(count, int) or count < 3 or not np.isfinite([lower, upper]).all() or lower >= upper:
            raise ValueError("require at least three nodes and finite increasing bounds")
        self.count = count
        self.lower, self.upper = lower, upper
        self.scale = 2 / (upper - lower)
        self.nodes = lower + (1 + np.cos(np.pi * np.arange(count) / (count - 1))) / self.scale
        self.coefficients = dct(np.eye(count), type=1, axis=0) / (count - 1)
        self.coefficients[[0, -1]] *= 0.5
        self.derivative = self.evaluate(self.nodes, 1)

    def evaluate(self, points, order=0):
        points = np.asarray(points)
        coefficients = cheb.chebder(self.coefficients, m=order, axis=0) * self.scale**order
        return cheb.chebvander((points - self.lower) * self.scale - 1, len(coefficients) - 1) @ coefficients


def radial_operators(grid):
    nodes, weights = leggauss(grid.count)
    nodes, weights = (nodes + 1) / 2, weights / 2
    radius = grid.nodes
    single = grid.evaluate((radius[:, None] * nodes).reshape(-1)).reshape(grid.count, grid.count, grid.count)
    integral = radius[:, None] * np.einsum("j,ijk->ik", weights, single)
    average = np.einsum("j,ijk->ik", weights, single)
    inverse_two = radius[:, None] * np.einsum("j,ijk->ik", weights * (1 - nodes), single)
    products = (nodes[:, None] * nodes).reshape(-1)
    product_weights = (weights[:, None] * weights).reshape(-1)
    double = grid.evaluate((radius[:, None] * products).reshape(-1)).reshape(grid.count, len(products), grid.count)
    inverse_one = radius[:, None] * np.einsum("j,ijk->ik", product_weights, double)
    return integral, average, inverse_one, inverse_two


def axis_data(schedule, eta, radial_parameter=512, sigma=0.2, peak=0.1):
    if not np.isfinite([radial_parameter, sigma, peak]).all() or min(radial_parameter, sigma, peak) <= 0:
        raise ValueError("Lambda, sigma and peak must be finite and positive")
    eta = np.asarray(eta)
    h = schedule.parameters.h
    growth, axial_exponent = 0.5 + h, 0.5 - h
    axis = 4 * eta + 0.025
    transport = axial_exponent * eta + (1 - eta**2) * axis
    denominator = 1 - 2 * h * eta**2
    zeta = -denominator * transport / (transport**2 + sigma**2)
    pressure = schedule.pressure(eta)
    source = (-growth * (1 - 2 * eta * axis) * axis - 4 * transport
              - (1 - eta**2) * pressure[1] + 4 * growth * eta * pressure[0])
    root = brentq(lambda value: axial_exponent * value + (1 - value**2) * (4 * value + 0.025), -1, 0, xtol=1e-15)

    def scalar_zeta(value):
        velocity = axial_exponent * value + (1 - value**2) * (4 * value + 0.025)
        return -(1 - 2 * h * value**2) * velocity / (velocity**2 + sigma**2)

    logs = np.array([np.log(peak) + radial_parameter * quad(scalar_zeta, root, float(value), epsabs=1e-13, epsrel=1e-13)[0] for value in eta.reshape(-1)]).reshape(eta.shape)
    with np.errstate(under="ignore"):
        swirl_squared = np.exp(2 * logs)
    return {"U": axis, "H": transport, "L": denominator, "Z": source, "zeta": zeta,
            "chi": transport**2 / (transport**2 + sigma**2), "pressure": pressure,
            "g2": swirl_squared, "log_g": logs, "eta0": root,
            "log_C": radial_parameter * quad(scalar_zeta, 0, root, epsabs=1e-13)[0] - np.log(peak)}


def solve_core(schedule, radial_count=17, eta_count=129, radial_parameter=512,
               sigma=0.2, peak=0.1, initial="comparison", iterations=80, tolerance=1e-11):
    if initial not in {"comparison", "flat"} or iterations < 1 or not np.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("require a known initial guess, positive iteration budget and tolerance")
    radial = ChebyshevGrid(radial_count, 0, 4.1)
    axial = ChebyshevGrid(eta_count, -1, 1)
    integral, average, inverse_one, inverse_two = radial_operators(radial)
    datum = axis_data(schedule, axial.nodes, radial_parameter, sigma, peak)
    radius, eta = radial.nodes[:, None], axial.nodes[None, :]
    h, growth, axial_exponent = schedule.parameters.h, 0.5 + schedule.parameters.h, 0.5 - schedule.parameters.h
    complement = 1 - eta**2
    phi_zero = comparison_function(radius * datum["chi"])
    correction_zero = -radius * datum["Z"] / (2 * datum["L"])
    phi = phi_zero.copy() if initial == "comparison" else np.ones_like(phi_zero)
    correction = correction_zero.copy() if initial == "comparison" else np.zeros_like(correction_zero)
    angular_inverse = np.linalg.inv(np.eye(radial_count)[None, :, :] + datum["chi"][:, None, None] * inverse_two[None, :, :] / 2)
    history = []
    status = "iteration_limit"
    for iteration in range(iterations):
        velocity = datum["U"] + correction / radial_parameter
        average_correction = average @ correction
        average_eta = average_correction @ axial.derivative.T
        transport_w = 1 - 4 * complement - 2 * axial_exponent * eta * datum["U"] + (-2 * axial_exponent * eta * average_correction - complement * average_eta) / radial_parameter
        transport_h = datum["H"] + complement * correction / radial_parameter
        phi_y, phi_eta = radial.derivative @ phi, phi @ axial.derivative.T
        correction_y, correction_eta = radial.derivative @ correction, correction @ axial.derivative.T
        pressure = integral @ (datum["g2"] * phi**2)
        pressure_eta = pressure @ axial.derivative.T
        remainder_one = ((transport_w + h * (1 - 2 * eta * velocity) + complement * correction * datum["zeta"]) * phi
                         + transport_w * radius * phi_y + transport_h * phi_eta) / datum["L"]
        remainder_two = (((growth * (1 - 4 * eta * datum["U"]) + 4 * complement) * correction
                          - 2 * growth * eta * correction**2 / radial_parameter
                          + transport_w * radius * correction_y + datum["H"] * correction_eta
                          + complement * correction * correction_eta / radial_parameter
                          - 4 * growth * eta * pressure + complement * pressure_eta
                          - 2 * eta * radius * datum["g2"] * phi**2) / datum["L"])
        next_phi = phi_zero + np.einsum("eij,je->ie", angular_inverse, inverse_two @ remainder_one) / (2 * radial_parameter)
        next_correction = correction_zero + inverse_one @ remainder_two / (2 * radial_parameter)
        increment = max(float(np.max(np.abs(next_phi - phi))), float(np.max(np.abs(next_correction - correction))) / radial_parameter)
        collocation = [2 * (radius * (radial.derivative @ phi_y) + 2 * phi_y) + datum["chi"] * phi - remainder_one / radial_parameter,
                   2 * (radius * (radial.derivative @ correction_y) + correction_y) + datum["Z"] / datum["L"] - remainder_two / radial_parameter,
                   radial.derivative @ pressure - datum["g2"] * phi**2]
        history.append({"iteration": iteration + 1, "increment_phi_or_U": increment,
                "input_iterate_rescaled_collocation_linf_not_independent": [float(np.max(np.abs(value))) for value in collocation],
                        "min_phi": float(np.min(next_phi)), "max_abs_delta_U": float(np.max(np.abs(next_correction))) / radial_parameter})
        if not np.all(np.isfinite(next_phi)) or not np.all(np.isfinite(next_correction)):
            status = "nonfinite_iterate"
            break
        if np.min(next_phi) <= 0:
            status = "phi_nonpositive"
            break
        if increment > 10:
            status = "iterate_growth_limit"
            break
        phi, correction = next_phi, next_correction
        if increment < tolerance:
            status = "increment_converged_not_yet_accepted"
            break
    return {"phi": phi, "u": correction, "p": integral @ (datum["g2"] * phi**2),
            "radial": radial, "axial": axial, "datum": datum, "history": history, "status": status,
            "Lambda": radial_parameter, "sigma": sigma, "peak": peak,
            "angular_matrix_condition_max": float(max(np.linalg.cond(matrix) for matrix in angular_inverse))}


def independent_residual(schedule, solution):
    radial, axial = solution["radial"], solution["axial"]
    radius = np.concatenate(([0.0], np.linspace(0.013, 4.087, 2 * radial.count), [4.1]))
    eta = np.linspace(-1, 1, 2 * axial.count + 1)
    radial_eval = [radial.evaluate(radius, order) for order in range(3)]
    eta_eval = [axial.evaluate(eta, order) for order in range(3)]

    def evaluate(values, radial_order=0, eta_order=0):
        return radial_eval[radial_order] @ values @ eta_eval[eta_order].T

    datum = axis_data(schedule, eta, solution["Lambda"], solution["sigma"], solution["peak"])
    phi = evaluate(solution["phi"])
    phi_y, phi_yy, phi_eta = evaluate(solution["phi"], 1), evaluate(solution["phi"], 2), evaluate(solution["phi"], 0, 1)
    radial_parameter = solution["Lambda"]
    velocity = datum["U"] + evaluate(solution["u"]) / radial_parameter
    velocity_y, velocity_yy = evaluate(solution["u"], 1) / radial_parameter, evaluate(solution["u"], 2) / radial_parameter
    velocity_eta = 4 + evaluate(solution["u"], 0, 1) / radial_parameter
    pressure = datum["pressure"][0] + evaluate(solution["p"]) / radial_parameter
    pressure_y = evaluate(solution["p"], 1) / radial_parameter
    pressure_eta = datum["pressure"][1] + evaluate(solution["p"], 0, 1) / radial_parameter
    nodes, weights = leggauss(radial.count + 3)
    average_values = sum(weight / 2 * (radial.evaluate(radius * (node + 1) / 2) @ solution["u"])
                         for node, weight in zip(nodes, weights))
    averaged = datum["U"] + average_values @ eta_eval[0].T / radial_parameter
    averaged_eta = 4 + average_values @ eta_eval[1].T / radial_parameter
    h = schedule.parameters.h
    growth, axial_exponent = 0.5 + h, 0.5 - h
    complement = 1 - eta**2
    transport_w = 1 - 2 * axial_exponent * eta * averaged - complement * averaged_eta
    transport_h = axial_exponent * eta + complement * velocity
    logarithmic_slope = 1 + radius[:, None] * phi_y / phi
    logarithmic_eta = radial_parameter * datum["zeta"] + phi_eta / phi
    angular_source = -transport_w * logarithmic_slope - h * (1 - 2 * eta * velocity) - transport_h * logarithmic_eta
    axial_source = (-transport_w * radius[:, None] * velocity_y - growth * (1 - 2 * eta * velocity) * velocity
                    - transport_h * velocity_eta - complement * pressure_eta + 4 * growth * eta * pressure
                    + 2 * eta * radius[:, None] * pressure_y)
    residuals = [-2 * datum["L"] * radial_parameter * (radius[:, None] * phi_yy + 2 * phi_y) / phi - angular_source,
                 -2 * datum["L"] * radial_parameter * (radius[:, None] * velocity_yy + velocity_y) - axial_source,
                 radial_parameter * pressure_y - datum["g2"] * phi**2]
    norms = [{"linf": float(np.max(np.abs(value))), "sampled_rms": float(np.sqrt(np.mean(value**2))),
              "l2_trapezoidal": float(np.sqrt(np.trapezoid(np.trapezoid(value**2, eta, axis=1), radius))),
              "axis_linf": float(np.max(np.abs(value[0]))), "outer_linf": float(np.max(np.abs(value[-1])))} for value in residuals]
    return {"equation_order": ["angular", "axial", "pressure"], "norms": norms,
            "off_grid_shape": [len(radius), len(eta)], "min_phi_off_grid": float(np.min(phi)),
            "max_abs_delta_U": float(np.max(np.abs(velocity - datum["U"]))),
            "first_term_error_U": float(np.max(np.abs(velocity - datum["U"] + radius[:, None] * datum["Z"] / (2 * datum["L"] * radial_parameter)))),
            "phi_comparison_error": float(np.max(np.abs(phi - comparison_function(radius[:, None] * datum["chi"])))),
            "max_pressure_correction": float(np.max(np.abs(pressure - datum["pressure"][0]))),
            "min_angular_source": float(np.min(angular_source))}