import numpy as np
import pytest

from nsblowup.compressed_not_theorem_admissible import CompressedNotTheoremAdmissibleSchedule
from nsblowup.core_representation import SpectralEta, exact_source, source_widths, factored_pressure, solve_factored
from nsblowup.core_not_theorem_admissible import ChebyshevGrid, radial_operators


@pytest.fixture(scope="module")
def schedule():
    return CompressedNotTheoremAdmissibleSchedule(lengths={"intermediate_power": 1, "axial_pulse_swirl_interval": 1,
        "angular_bump_interval_unbumped": 1, "profile_interpolation": 8, "release_hold": 2})


def test_exact_source_derivatives(schedule):
    root = source_widths(schedule)["eta0"]
    points = root + np.linspace(-0.005, 0.005, 9)
    exact = exact_source(schedule, points)
    errors = []
    for step in (0.0002, 0.0001, 0.00005):
        values = [exact_source(schedule, points + offset * step)["g2"] for offset in (-2, -1, 0, 1, 2)]
        first = (values[0] - 8 * values[1] + 8 * values[3] - values[4]) / (12 * step)
        second = (-values[0] + 16 * values[1] - 30 * values[2] + 16 * values[3] - values[4]) / (12 * step**2)
        errors.append([np.max(np.abs(first - exact["g2_eta"])), np.max(np.abs(second - exact["g2_etaeta"]))])
    assert np.all(np.array(errors[:-1]) / np.array(errors[1:]) > 14)
    assert np.all(exact["g2"] >= 0)
    widths = source_widths(schedule)
    assert 0.00416 < widths["g_standard_deviation_local"] < 0.00418
    assert 0.00294 < widths["g2_standard_deviation_local"] < 0.00296


def test_transform_derivatives_converge():
    points = np.linspace(-1, 1, 301)
    errors = []
    for count in (9, 17, 33):
        grid = SpectralEta(count)
        values = np.exp(3 * grid.nodes)
        errors.append([np.max(np.abs(grid.evaluate(values, points, order) - 3**order * np.exp(3 * points))) for order in (1, 2)])
        np.testing.assert_allclose(grid.differentiate(values, 1), grid.evaluate(values, grid.nodes, 1), atol=1e-11)
        np.testing.assert_allclose(grid.resample(values, 65, 2), grid.evaluate(values, SpectralEta(65).nodes, 2), atol=1e-10)
    assert np.all(np.array(errors[1:]) < np.array(errors[:-1]))


def test_source_interpolation_convergence(schedule):
    root = source_widths(schedule)["eta0"]
    points = root + np.linspace(-0.03, 0.03, 801)
    exact = exact_source(schedule, points)
    errors = []
    for count in (513, 1025, 2049):
        grid = SpectralEta(count)
        values = exact_source(schedule, grid.nodes)["g2"]
        errors.append([np.max(np.abs(grid.evaluate(values, points, order) - exact[key])) for order, key in enumerate(("g2", "g2_eta", "g2_etaeta"))])
    assert np.all(np.array(errors[1:]) < np.array(errors[:-1]))
    assert errors[-1][0] / 0.01 < 1e-4


def test_factored_pressure_and_independent_radial_identity():
    eta_grid = SpectralEta(65)
    eta = eta_grid.nodes
    datum = {"g2": np.exp(eta), "g2_eta": np.exp(eta), "g2_etaeta": np.exp(eta)}
    points = np.linspace(0, 4.1, 103)
    errors = []
    for count in (5, 9, 17):
        radial = ChebyshevGrid(count, 0, 4.1)
        integral = radial_operators(radial)[0]
        phi = np.exp(radial.nodes[:, None] / 4) * (1 + .1 * eta)
        phi_eta = np.exp(radial.nodes[:, None] / 4) * np.full_like(eta, .1)
        result = factored_pressure(phi, phi_eta, np.zeros_like(phi), integral, datum)
        np.testing.assert_allclose(result["p"], datum["g2"] * result["Pbar"], atol=1e-14)
        np.testing.assert_allclose(eta_grid.differentiate(result["p"]), result["p_eta"], atol=1e-10)
        np.testing.assert_allclose(eta_grid.differentiate(result["p"], 2), result["p_etaeta"], atol=1e-7)
        exact_square = np.exp(points[:, None] / 2) * (1 + .1 * eta)**2
        errors.append(np.max(np.abs(radial.evaluate(points, 1) @ result["Pbar"] - exact_square)))
    assert errors[1] < errors[0] / 100
    assert errors[2] < errors[1] / 100


def test_flat_zero_field_modal_history_is_finite(schedule):
    import json

    result = solve_factored(schedule, radial_count=17, eta_count=65, initial="flat", iterations=1)
    assert result["history"][0]["eta_modal_tail_ratio"]["u"] == 0
    json.dumps(result["history"], allow_nan=False)