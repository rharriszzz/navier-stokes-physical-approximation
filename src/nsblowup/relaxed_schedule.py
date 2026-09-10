"""Appendix A scheduled swirl with relaxed hierarchy, NOT theorem-admissible.

Exact equation mappings and deliberate omissions: notes/equation-map.md.
"""

from dataclasses import dataclass

import numpy as np
from scipy.integrate import quad, quad_vec, solve_ivp
from scipy.optimize import brentq
from scipy.special import expit, logsumexp

from nsblowup.coordinates import validate_h


def smooth_step(coordinate, derivative=0):
    """Evaluate (A.5) and its first two derivatives, including flat ends."""
    coordinate = np.asarray(coordinate, dtype=np.float64)
    if not np.all(np.isfinite(coordinate)) or derivative not in (0, 1, 2):
        raise ValueError("step needs finite coordinates and derivative 0, 1, or 2")
    result = np.zeros_like(coordinate)
    if derivative == 0:
        result[coordinate >= 1] = 1.0
    interior = (coordinate > 0) & (coordinate < 1)
    interior_coordinate = coordinate[interior]
    with np.errstate(over="ignore", divide="ignore", under="ignore"):
        argument = (1 - interior_coordinate) ** -2 - interior_coordinate**-2
    values = expit(argument)
    if derivative:
        active = np.abs(argument) < 600
        local = interior_coordinate[active]
        argument_first = 2 * ((1 - local) ** -3 + local**-3)
        weight = expit(argument[active]) * expit(-argument[active])
        differentiated = weight * argument_first
        if derivative == 2:
            argument_second = 6 * ((1 - local) ** -4 - local**-4)
            differentiated = weight * (argument_second + (1 - 2 * values[active]) * argument_first**2)
        values = np.zeros_like(values)
        values[active] = differentiated
    result[interior] = values
    return result


@dataclass(frozen=True)
class RelaxedParameters:
    axial_reduction: float = 1.0
    pressure_amplitude: float = 2.0
    outer_decay: float = 0.2
    h: float = 0.005
    interpolation_length: float = 64.0
    terminal_coefficient: float = 0.025

    def __post_init__(self):
        validate_h(self.h)
        values = (self.axial_reduction, self.pressure_amplitude, self.outer_decay,
                  self.interpolation_length, self.terminal_coefficient)
        if not all(np.isfinite(value) and value > 0 for value in values):
            raise ValueError("relaxed schedule parameters must be finite and positive")
        if not self.h < self.outer_decay < 1:
            raise ValueError("retain 0 < h < lambda < 1")
        if 60 * np.log(1 / self.outer_decay) <= 25:
            raise ValueError("reserved intervals do not fit in T_w")
        if self.axial_reduction > 20:
            raise ValueError("M_d exceeds this finite experiment's log-span budget")
        if self.terminal_coefficient * self.h >= 1:
            raise ValueError("terminal factor must stay positive")
        if 8 * np.log(2) / self.interpolation_length > 0.1:
            raise ValueError("T_f violates the interpolation slope bound")
        if 4 * self.terminal_coefficient / (1 - self.terminal_coefficient * self.h) >= 0.25:
            raise ValueError("c_o violates the terminal logarithmic slope bound")


@dataclass
class ScheduleStage:
    name: str
    start: float
    length: float
    log_start: float
    exponent: float
    slope_start: float
    slope_end: float
    kind: str
    primitive: object
    parameters: RelaxedParameters

    def log_swirl(self, local, eta, derivative=0):
        """Return log E or its first/second local-y derivative on this stage."""
        local, eta = np.broadcast_arrays(np.asarray(local, dtype=np.float64), np.asarray(eta, dtype=np.float64))
        if derivative not in (0, 1, 2) or not np.all(np.isfinite(local)) or not np.all(np.isfinite(eta)):
            raise ValueError("finite coordinates and derivative 0, 1, or 2 required")
        if np.any((local < 0) | (local > self.length)) or np.any(np.abs(eta) > 1):
            raise ValueError("stage coordinates out of bounds")
        logarithm = np.log1p(eta**2)
        if self.kind == "interpolation":
            position = local / self.length
            if derivative == 0:
                return self.log_start + (self.slope_start - 0.5) * local - logarithm - smooth_step(position) * (np.log(2) - logarithm)
            if derivative == 1:
                return self.slope_start - 0.5 - smooth_step(position, 1) * (np.log(2) - logarithm) / self.length
            return -smooth_step(position, 2) * (np.log(2) - logarithm) / self.length**2
        if self.kind == "terminal":
            density = self.parameters.terminal_coefficient * self.parameters.h
            position = (local - 1) / 2
            factor = 1 - density * (1 - smooth_step(position))
            first = density * smooth_step(position, 1) / 2
            if derivative == 0:
                return self.log_start + (self.slope_start - 0.5) * local + np.log(factor) - np.log1p(-density)
            if derivative == 1:
                return self.slope_start - 0.5 + first / factor
            return density * smooth_step(position, 2) / (4 * factor) - (first / factor)**2
        difference = self.slope_end - self.slope_start
        if derivative == 0:
            integral = 0.0 if difference == 0 else difference * self.primitive(local.reshape(-1))[0].reshape(local.shape)
            return self.log_start + (self.slope_start - 0.5) * local + integral - self.exponent * logarithm
        if derivative == 1:
            return np.full_like(local, self.slope_start - 0.5) + difference * smooth_step(local)
        return difference * smooth_step(local, 1)

    def eta_exponent(self, local):
        if self.kind == "interpolation":
            return 1 - smooth_step(np.asarray(local, dtype=np.float64) / self.length)
        return np.zeros_like(np.asarray(local, dtype=np.float64)) + self.exponent


class RelaxedSchedule:
    """Finite unbumped scheduled swirl of (A.21), not a completed exterior."""

    def __init__(self, parameters=None, rtol=1e-10, atol=1e-12):
        self.parameters = parameters or RelaxedParameters()
        if not all(np.isfinite(value) and 0 < value < 1 for value in (rtol, atol)):
            raise ValueError("positive finite tolerances below one required")
        self.rtol, self.atol = rtol, atol
        primitive = solve_ivp(lambda position, _state: [float(smooth_step(position))],
                              (0, 1), [0.0], method="DOP853", rtol=rtol, atol=atol,
                              max_step=0.025, dense_output=True)
        if not primitive.success:
            raise RuntimeError("step primitive failed: " + primitive.message)
        self.primitive = primitive.sol
        self.primitive_evaluations = primitive.nfev
        self.stages = []
        self.q_paths = []
        self._construct()

    def _add(self, name, length, exponent, slope_start, slope_end=None, kind="constant"):
        if not np.isfinite(length) or length <= 0:
            raise ValueError("schedule intervals must have finite positive lengths")
        if self.stages:
            previous = self.stages[-1]
            start = previous.start + previous.length
            log_start = float(previous.log_swirl(previous.length, 0))
        else:
            start, log_start = 0.0, np.log(self.parameters.pressure_amplitude)
        stage = ScheduleStage(name, start, length, log_start, exponent, slope_start,
                              slope_start if slope_end is None else slope_end, kind,
                              self.primitive, self.parameters)
        self.stages.append(stage)
        return stage

    def _advance_q(self, stage, initial):
        def equation(position, state):
            slope = float(stage.log_swirl(position, 0, 1)) + 0.5
            return [-(1 + slope) * state[0] - slope - self.parameters.h]

        solution = solve_ivp(equation, (0, stage.length), [initial], method="DOP853",
                             rtol=self.rtol, atol=self.atol, max_step=0.025, dense_output=True)
        if not solution.success:
            raise RuntimeError("Q evolution failed: " + solution.message)
        self.q_paths.append((stage, solution))
        return float(solution.y[0, -1])

    def _construct(self):
        parameters = self.parameters
        decay, h = parameters.outer_decay, parameters.h
        self.axial_length = float(np.exp(parameters.axial_reduction) + 10)
        self.power_length = float(60 * np.log(1 / decay))
        self._add("inner_slope_transition", 1.0, 1.0, 0.6, 0.0, "ramp")
        self._add("axial_reduction", self.axial_length, 1.0, 0.0)
        self._add("power_slope_transition", 1.0, 1.0, 0.0, -decay, "ramp")
        self._add("intermediate_power", self.power_length, 1.0, -decay)
        self._add("axial_pulse_swirl_interval", 13 / decay, 1.0, -decay)
        self._add("profile_interpolation", parameters.interpolation_length, 1.0, -decay, kind="interpolation")
        self._add("angular_bump_interval_unbumped", 30 * np.log(1 / decay), 0.0, -decay)
        self.q_initial = (decay - h) / (1 - decay)
        release = self._add("release_down", 1.0, 0.0, -decay, -1.0, "ramp")
        self.q_after_down = self._advance_q(release, self.q_initial)
        release_hold = self._add("release_hold", 4 * np.log(1 / h), 0.0, -1.0)
        self.q_after_hold = self.q_after_down + (1 - h) * release_hold.length
        release_up = self._add("release_up", 1.0, 0.0, -1.0, -h, "ramp")
        self.q_before_stop = self._advance_q(release_up, self.q_after_hold)
        density = parameters.terminal_coefficient * h
        self.q_target, self.q_target_error = quad(
            lambda position: np.exp((1 - h) * position) * density * float(smooth_step((position - 1) / 2, 1)) / (2 * (1 - density)),
            1, 3, epsabs=self.atol, epsrel=self.rtol,
        )
        if not 0 < self.q_target < self.q_before_stop:
            raise ValueError("Q stopping event requires 0 < Q_p < Q_start")
        self.q_stop_length = float(np.log(self.q_before_stop / self.q_target) / (1 - h))
        self._add("q_stopping_hold", self.q_stop_length, 0.0, -h)
        terminal = self._add("terminal_collar", 3.0, 0.0, -h, kind="terminal")
        self.q_terminal = self._advance_q(terminal, self.q_target)
        self.span = terminal.start + terminal.length
        self.log_tail = float(terminal.log_swirl(terminal.length, 0))
        self.decades = self.span / np.log(10)

    def log_swirl(self, coordinate, eta=0.0):
        """Evaluate the entire positive schedule in log amplitude, including tails."""
        coordinate, eta = np.broadcast_arrays(np.asarray(coordinate, dtype=np.float64), np.asarray(eta, dtype=np.float64))
        if not np.all(np.isfinite(coordinate)) or not np.all(np.isfinite(eta)) or np.any(np.abs(eta) > 1):
            raise ValueError("finite y and |eta| <= 1 required")
        result = np.empty_like(coordinate)
        inner = coordinate < 0
        result[inner] = np.log(self.parameters.pressure_amplitude) + coordinate[inner] / 10 - np.log1p(eta[inner]**2)
        for stage in self.stages:
            selected = (coordinate >= stage.start) & (coordinate < stage.start + stage.length)
            if np.any(selected):
                result[selected] = stage.log_swirl(coordinate[selected] - stage.start, eta[selected])
        tail = coordinate >= self.span
        result[tail] = self.log_tail - (0.5 + self.parameters.h) * (coordinate[tail] - self.span)
        return result

    def pressure(self, eta, return_details=False):
        """Full (A.21) datum and two analytic eta derivatives, without tail truncation."""
        eta = np.asarray(eta, dtype=np.float64)
        if eta.size == 0 or not np.all(np.isfinite(eta)) or np.any(np.abs(eta) > 1):
            raise ValueError("pressure requires nonempty finite eta in [-1, 1]")
        logarithm = np.log1p(eta**2)
        inner = 2 * np.log(self.parameters.pressure_amplitude) + np.log(5) - 2 * logarithm
        logarithmic_moments = [np.stack([inner, inner, inner])]
        details = [{"name": "infinite_inner", "log_integral_eta0": float(2 * np.log(self.parameters.pressure_amplitude) + np.log(5)),
                    "method": "analytic", "normalized_quadrature_error": 0.0}]
        for stage in self.stages:
            if stage.kind == "constant":
                rate = 2 * stage.slope_start - 1
                integral = -np.expm1(rate * stage.length) / -rate
                zeroth = integral * np.exp(-2 * stage.exponent * logarithm)
                moments = np.stack([zeroth, stage.exponent * zeroth, stage.exponent**2 * zeroth])
                error, method = 0.0, "analytic"
                integral_eta0 = integral
            else:
                def integrand(position):
                    exponent = stage.eta_exponent(position)
                    value = np.exp(2 * (stage.log_swirl(position, eta) - stage.log_start))
                    return np.stack([value, exponent * value, exponent**2 * value])

                moments, error, info = quad_vec(integrand, 0, stage.length, epsabs=self.atol,
                                                epsrel=self.rtol, norm="max", full_output=True)
                if not info.success:
                    raise RuntimeError(f"pressure quadrature failed on {stage.name}: {info.message}")
                integral_eta0 = quad(lambda position: np.exp(2 * (float(stage.log_swirl(position, 0)) - stage.log_start)),
                                    0, stage.length, epsabs=self.atol, epsrel=self.rtol)[0]
                method = "adaptive quadrature of locally normalized moments"
            if np.any(moments < 0) or not np.all(np.isfinite(moments)) or np.any(moments[0] <= 0):
                raise FloatingPointError("invalid normalized pressure moments")
            with np.errstate(divide="ignore"):
                logarithmic_moments.append(2 * stage.log_start + np.log(moments))
            details.append({"name": stage.name, "log_integral_eta0": float(2 * stage.log_start + np.log(integral_eta0)),
                            "method": method, "normalized_quadrature_error": float(error)})
        tail = np.full_like(eta, 2 * self.log_tail - np.log1p(2 * self.parameters.h))
        logarithmic_moments.append(np.stack([tail, np.full_like(eta, -np.inf), np.full_like(eta, -np.inf)]))
        details.append({"name": "infinite_outer", "log_integral_eta0": float(2 * self.log_tail - np.log1p(2 * self.parameters.h)),
                        "method": "analytic", "normalized_quadrature_error": 0.0})
        with np.errstate(under="ignore", over="raise", invalid="raise"):
            total = np.exp(logsumexp(np.stack(logarithmic_moments), axis=0))
        first = 2 * eta / (1 + eta**2)
        second = 2 * (1 - eta**2) / (1 + eta**2)**2
        values = np.stack([-0.5 * total[0], first * total[1], second * total[1] - 2 * first**2 * total[2]])
        if not np.all(np.isfinite(values)) or np.any(values[0] >= 0):
            raise FloatingPointError("pressure not representable in float64")
        return (values, details) if return_details else values


def axial_diagnostic(schedule, eta, axial_offset=0.025):
    """Evaluate (B.1) and its H_star root; this does not solve (B.15)."""
    if not np.isfinite(axial_offset) or not 0 < axial_offset <= 0.05:
        raise ValueError("require 0 < j0 <= 0.05")
    eta = np.asarray(eta, dtype=np.float64)
    growth = 0.5 + schedule.parameters.h
    axial_exponent = 0.5 - schedule.parameters.h

    def transport(position):
        return axial_exponent * position + (1 - position**2) * (4 * position + axial_offset)

    root, root_info = brentq(transport, -1, 0, xtol=1e-15, full_output=True)
    pressure = schedule.pressure(eta)
    root_pressure = schedule.pressure(root)

    def source(position, datum):
        axis = 4 * position + axial_offset
        return (-growth * (1 - 2 * position * axis) * axis - 4 * transport(position)
                - (1 - position**2) * datum[1] + 4 * growth * position * datum[0])

    return {
        "pressure": pressure, "z_star": source(eta, pressure), "eta0": float(root),
        "root_iterations": root_info.iterations, "root_residual": float(transport(root)),
        "root_pressure": root_pressure, "root_z_star": float(source(root, root_pressure)),
    }


def first_axial_correction(eta, z_star, radial_parameter, h=0.005, scaled_radius=4.0):
    """First explicit B.13 term only, not a finite-Lambda nonlinear error estimate."""
    validate_h(h)
    if not np.isfinite(radial_parameter) or radial_parameter < 1 or not np.isfinite(scaled_radius) or not 0 <= scaled_radius <= 4.1:
        raise ValueError("require finite Lambda >= 1 and 0 <= Y <= 4.1")
    eta, z_star = np.broadcast_arrays(np.asarray(eta, dtype=np.float64), np.asarray(z_star, dtype=np.float64))
    if not np.all(np.isfinite(eta)) or not np.all(np.isfinite(z_star)) or np.any(np.abs(eta) > 1):
        raise ValueError("finite Z_star and |eta| <= 1 required")
    return -scaled_radius * z_star / (2 * (1 - 2 * h * eta**2) * radial_parameter)