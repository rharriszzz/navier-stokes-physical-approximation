import numpy as np
import pytest

from nsblowup.coordinates import to_physical
from nsblowup.profiles import ComparisonParameters, comparison_function, comparison_profiles, velocity


def test_comparison_function_against_published_series():
    argument = np.linspace(0.0, 4.1, 100)
    series = np.ones_like(argument)
    term = np.ones_like(argument)
    for degree in range(1, 30):
        term *= (-argument / 2) / (degree * (degree + 1))
        series += term
    np.testing.assert_allclose(comparison_function(argument), series, rtol=2e-15)
    assert comparison_function(0.0) == 1.0
    assert np.min(comparison_function(argument)) > 0.265


def test_axis_data_and_radial_identity():
    parameters = ComparisonParameters()
    eta = np.linspace(-0.1, 0.1, 25)
    swirl, axial, radial_coefficient = comparison_profiles(0.0, eta, parameters)
    np.testing.assert_array_equal(swirl, 0.0)
    np.testing.assert_allclose(axial, 4 * eta + parameters.axial_offset)
    radius, physical_axial, scale = to_physical(0.0, eta, 0.01, parameters.h)
    radial_velocity, swirl_velocity, axial_velocity = velocity(radius, physical_axial, 0.01, parameters)
    np.testing.assert_array_equal(radial_velocity, 0.0)
    np.testing.assert_array_equal(swirl_velocity, 0.0)
    assert np.all(np.isfinite(axial_velocity))
    expected = (2 * eta * axial - 2 * (0.5 - parameters.h) * eta * axial - 4 * (1 - eta**2))
    np.testing.assert_allclose(radial_coefficient, expected / (1 - 2 * parameters.h * eta**2))


@pytest.mark.parametrize("tau", [1.0, 1e-3, 1e-6])
def test_stationary_rescaled_components(tau):
    parameters = ComparisonParameters()
    radial_similarity = np.linspace(0.0, 4.0 / parameters.radial_parameter, 33)[:, None]
    eta = np.linspace(-0.12, 0.12, 41)[None, :]
    radius, axial, scale = to_physical(radial_similarity, eta, tau, parameters.h)
    radial_velocity, swirl_velocity, axial_velocity = velocity(radius, axial, tau, parameters)
    swirl, axial_profile, radial_coefficient = comparison_profiles(radial_similarity, eta, parameters)
    np.testing.assert_allclose(swirl_velocity * scale ** (0.5 + parameters.h), swirl, atol=2e-15)
    np.testing.assert_allclose(axial_velocity * scale ** (0.5 + parameters.h), axial_profile, atol=2e-15)
    np.testing.assert_allclose(radial_velocity * np.sqrt(scale), radial_coefficient * np.sqrt(radial_similarity / 2), atol=2e-15)
    assert radial_velocity.dtype == np.float64


@pytest.mark.parametrize("values", [{"sigma": 0}, {"radial_parameter": 0}, {"axial_offset": 0.1}, {"swirl_peak": 2}])
def test_invalid_parameters(values):
    with pytest.raises(ValueError):
        ComparisonParameters(**values)


def test_comparison_not_extrapolated():
    with pytest.raises(ValueError):
        comparison_profiles(1.0, 0.0, ComparisonParameters())