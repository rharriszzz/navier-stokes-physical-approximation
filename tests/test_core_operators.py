import numpy as np
import pytest

from nsblowup.core_not_theorem_admissible import ChebyshevGrid, radial_operators, solve_core, independent_residual, axis_data
from nsblowup.compressed_not_theorem_admissible import CompressedNotTheoremAdmissibleSchedule


def test_spectral_polynomial_derivatives():
    grid = ChebyshevGrid(17, -1, 1)
    values = grid.nodes**5 - 2 * grid.nodes**2
    points = np.linspace(-0.99, 0.99, 39)
    np.testing.assert_allclose(grid.evaluate(points) @ values, points**5 - 2 * points**2, atol=1e-13)
    np.testing.assert_allclose(grid.evaluate(points, 1) @ values, 5 * points**4 - 4 * points, atol=1e-11)
    np.testing.assert_allclose(grid.evaluate(points, 2) @ values, 20 * points**3 - 4, atol=1e-9)


def test_radial_inverse_monomials_and_axis():
    grid = ChebyshevGrid(17, 0, 4.1)
    integral, average, inverse_one, inverse_two = radial_operators(grid)
    for degree in range(9):
        values = (grid.nodes / 4.1)**degree
        primitive = grid.nodes * values
        np.testing.assert_allclose(integral @ values, primitive / (degree + 1), atol=1e-12)
        np.testing.assert_allclose(average @ values, values / (degree + 1), atol=1e-12)
        for index, inverse in enumerate((inverse_one, inverse_two), start=1):
            np.testing.assert_allclose(inverse @ values, primitive / ((degree + 1) * (degree + index)), atol=1e-12)
            assert (inverse @ values)[-1] == 0


def test_angular_resolvent_and_comparison():
    from nsblowup.profiles import comparison_function

    grid = ChebyshevGrid(25, 0, 4.1)
    inverse_two = radial_operators(grid)[3]
    for chi in (0, 0.1, 0.99):
        operator = np.eye(grid.count) + chi * inverse_two / 2
        phi = np.linalg.solve(operator, np.ones(grid.count))
        np.testing.assert_allclose(phi, comparison_function(grid.nodes * chi), atol=2e-13)


def test_small_core_increment_is_not_equation_acceptance():
    schedule = CompressedNotTheoremAdmissibleSchedule(lengths={
        "intermediate_power": 1, "axial_pulse_swirl_interval": 1,
        "angular_bump_interval_unbumped": 1, "profile_interpolation": 8, "release_hold": 2})
    solution = solve_core(schedule)
    np.testing.assert_array_equal(solution["phi"][-1], 1)
    np.testing.assert_array_equal(solution["u"][-1], 0)
    np.testing.assert_array_equal(solution["p"][-1], 0)
    assert solution["status"] == "increment_converged_not_yet_accepted"
    residual = independent_residual(schedule, solution)
    assert residual["norms"][0]["linf"] > 1
    assert residual["norms"][2]["linf"] > 1e-3
    assert residual["min_phi_off_grid"] > 0
    assert len(solution["history"][0]["input_iterate_rescaled_collocation_linf_not_independent"]) == 3
    at_root = axis_data(schedule, np.array([solution["datum"]["eta0"]]))
    np.testing.assert_allclose(at_root["g2"], 0.01, atol=1e-15)
    np.testing.assert_allclose(at_root["H"], 0, atol=1e-14)
    with pytest.raises(ValueError):
        solve_core(schedule, initial="unknown")
    with pytest.raises(ValueError):
        axis_data(schedule, np.array([0.0]), sigma=0)