import numpy as np
import pytest
from scipy.integrate import quad

from nsblowup.relaxed_schedule import (
    RelaxedParameters, RelaxedSchedule, axial_diagnostic, first_axial_correction, smooth_step,
)


def test_published_step_and_derivatives():
    position = np.linspace(0.05, 0.95, 91)
    numerator = np.exp(-1 / position**2)
    expected = numerator / (numerator + np.exp(-1 / (1 - position)**2))
    np.testing.assert_allclose(smooth_step(position), expected, atol=2e-15)
    np.testing.assert_allclose(smooth_step(position) + smooth_step(1 - position), 1, atol=2e-15)
    assert smooth_step(0.5, 1) == 8
    assert np.max(smooth_step(np.linspace(0, 1, 10001), 1)) <= 8
    for order in (0, 1, 2):
        assert np.all(np.isfinite(smooth_step([0, 1e-200, 0.5, 1, 2], order)))
    for order in (1, 2):
        np.testing.assert_array_equal(smooth_step([0, 1], order), [0, 0])
        spacing = 1e-6
        numerical = (smooth_step(position + spacing, order - 1) - smooth_step(position - spacing, order - 1)) / (2 * spacing)
        np.testing.assert_allclose(numerical, smooth_step(position, order), atol=1e-7)


@pytest.fixture(scope="module")
def schedule():
    return RelaxedSchedule()


def test_stage_joins_and_positive_representation(schedule):
    assert len(schedule.stages) == 12
    for left, right in zip(schedule.stages[:-1], schedule.stages[1:]):
        assert left.start + left.length == right.start
        for order in (0, 1, 2):
            np.testing.assert_allclose(left.log_swirl(left.length, [-1, -0.3, 0, 1], order),
                                       right.log_swirl(0, [-1, -0.3, 0, 1], order), atol=2e-12)
    assert schedule.stages[0].log_swirl(0, 0, 1) == pytest.approx(0.1)
    assert schedule.stages[-1].log_swirl(3, 0, 1) == pytest.approx(-0.5 - schedule.parameters.h)
    log_values = schedule.log_swirl(np.linspace(-20, schedule.span + 20, 1001), 0.5)
    assert np.all(np.isfinite(log_values))
    assert np.all(np.exp(log_values) > 0)
    assert schedule.decades == pytest.approx(schedule.span / np.log(10))


def test_primitive_against_independent_quadrature(schedule):
    for position in np.linspace(0, 1, 17):
        expected = quad(lambda value: float(smooth_step(value)), 0, position, epsabs=1e-13)[0]
        np.testing.assert_allclose(schedule.primitive(position)[0], expected, atol=2e-12)


def test_q_independent_integrating_factor(schedule):
    for stage, solution in schedule.q_paths:
        def exponent(position):
            return 1.5 * position + float(stage.log_swirl(position, 0) - stage.log_swirl(0, 0))

        integral = quad(lambda position: np.exp(exponent(position)) *
                        (-float(stage.log_swirl(position, 0, 1)) - 0.5 - schedule.parameters.h),
                        0, stage.length, epsabs=1e-12, epsrel=1e-11)[0]
        expected = np.exp(-exponent(stage.length)) * (solution.y[0, 0] + integral)
        np.testing.assert_allclose(solution.y[0, -1], expected, atol=2e-10)
    np.testing.assert_allclose(schedule.q_before_stop * np.exp(-(1 - schedule.parameters.h) * schedule.q_stop_length), schedule.q_target, rtol=1e-14)
    assert abs(schedule.q_terminal) < 1e-11


@pytest.mark.parametrize("values", [{"outer_decay": 0.005}, {"outer_decay": 0.9}, {"interpolation_length": 1},
                                       {"terminal_coefficient": 1}, {"pressure_amplitude": 0}, {"h": 0.01}])
def test_invalid_schedule_choices(values):
    with pytest.raises(ValueError):
        RelaxedParameters(**values)


def test_full_pressure_independent_quadrature(schedule):
    eta = np.array([-1, -0.4, 0, 0.4, 1])
    pressure, details = schedule.pressure(eta, return_details=True)
    direct = []
    for position in eta:
        inner = quad(lambda radius: np.exp(2 * float(schedule.log_swirl(radius, position))), -np.inf, 0, epsabs=1e-12)[0]
        outer = sum(quad(lambda radius: np.exp(2 * float(schedule.log_swirl(radius, position))),
                         stage.start, stage.start + stage.length, epsabs=1e-12)[0] for stage in schedule.stages)
        tail_scaled = quad(lambda distance: np.exp(-(1 + 2 * schedule.parameters.h) * distance), 0, np.inf)[0]
        direct.append(-0.5 * (inner + outer + np.exp(2 * schedule.log_tail) * tail_scaled))
    np.testing.assert_allclose(pressure[0], direct, rtol=2e-11)
    assert len(details) == 14
    assert all(np.isfinite(record["log_integral_eta0"]) for record in details)
    assert np.all(pressure[0] < -2.5 * schedule.parameters.pressure_amplitude**2 / (1 + eta**2)**2)
    np.testing.assert_allclose(pressure[0], pressure[0, ::-1], atol=1e-13)
    assert np.all(eta[eta != 0] * pressure[1, eta != 0] > 0)


def test_pressure_derivative_and_tolerance_convergence(schedule):
    eta = np.linspace(-0.98, 0.98, 31)
    values = schedule.pressure(eta)
    refined = RelaxedSchedule(rtol=1e-12, atol=1e-14)
    np.testing.assert_allclose(values, refined.pressure(eta), rtol=2e-10, atol=1e-11)
    errors = []
    for spacing in (0.004, 0.002, 0.001):
        plus, minus = schedule.pressure(eta + spacing)[0], schedule.pressure(eta - spacing)[0]
        differences = np.stack([(plus - minus) / (2 * spacing), (plus - 2 * values[0] + minus) / spacing**2])
        errors.append(np.max(np.abs(differences - values[1:]), axis=1))
    assert np.all(np.array(errors[:-1]) / np.array(errors[1:]) > 3.9)
    assert np.max(errors[-1] / np.max(np.abs(values[1:]), axis=1)) < 4e-6


def test_tail_integrals_retained_below_float64_amplitude_range():
    schedule = RelaxedSchedule(RelaxedParameters(outer_decay=0.05))
    pressure, details = schedule.pressure([0, 0.4], return_details=True)
    assert details[-1]["log_integral_eta0"] < np.log(np.finfo(float).tiny)
    assert np.all(np.isfinite(pressure))
    assert details[-1]["method"] == "analytic"


def test_first_correction_formula_and_scaling(schedule):
    eta = np.linspace(-1, 1, 33)
    diagnostic = axial_diagnostic(schedule, eta)
    assert -1 < diagnostic["eta0"] < 0
    assert abs(diagnostic["root_residual"]) < 1e-14
    axis = 4 * eta + 0.025
    growth = 0.505
    transport = 0.495 * eta + (1 - eta**2) * axis
    expected = (-growth * (1 - 2 * eta * axis) * axis - 4 * transport
                - (1 - eta**2) * diagnostic["pressure"][1] + 4 * growth * eta * diagnostic["pressure"][0])
    np.testing.assert_allclose(diagnostic["z_star"], expected)
    correction = first_axial_correction(eta, expected, 32)
    np.testing.assert_allclose(correction, -expected / (16 * (1 - 0.01 * eta**2)))
    np.testing.assert_allclose(first_axial_correction(eta, expected, 128), correction / 4)
    np.testing.assert_array_equal(first_axial_correction(eta, expected, 32, scaled_radius=0), 0)