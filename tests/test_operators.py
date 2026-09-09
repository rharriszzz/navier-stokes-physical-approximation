import numpy as np
import pytest

from nsblowup.operators_axisymmetric import divergence
from nsblowup.profiles import ComparisonParameters, comparison_profiles, velocity
from nsblowup.coordinates import to_similarity


@pytest.mark.parametrize("radial_start", [0.0, 0.1])
def test_linear_field_and_axis(radial_start):
    radius = np.linspace(radial_start, 1, 33)
    axial = np.linspace(-1, 1, 65)
    radial_mesh, axial_mesh = np.meshgrid(radius, axial, indexing="ij")
    np.testing.assert_allclose(divergence(radius, axial, 2 * radial_mesh, 3 * axial_mesh), 7, atol=1e-12)
    np.testing.assert_allclose(divergence(radius, axial, -radial_mesh, 2 * axial_mesh), 0, atol=1e-12)


def test_divergence_free_manufactured_convergence():
    errors = []
    for radial_count in (17, 33, 65):
        radius = np.linspace(0, 1, radial_count)
        axial = np.linspace(-1, 1, 2 * radial_count - 1)
        radial_mesh, axial_mesh = np.meshgrid(radius, axial, indexing="ij")
        radial_velocity = -radial_mesh * np.exp(-radial_mesh**2) * np.cos(axial_mesh)
        axial_velocity = 2 * (1 - radial_mesh**2) * np.exp(-radial_mesh**2) * np.sin(axial_mesh)
        actual = divergence(radius, axial, radial_velocity, axial_velocity)
        assert np.all(np.isfinite(actual[0]))
        errors.append(np.max(np.abs(actual)))
    orders = np.log2(np.array(errors[:-1]) / errors[1:])
    assert np.all(orders > 1.85), (errors, orders)


def test_nonzero_manufactured_divergence_convergence():
    errors = []
    for count in (17, 33, 65):
        radius = np.linspace(0, 1, count)
        axial = np.linspace(-1, 1, count)
        radial_mesh, axial_mesh = np.meshgrid(radius, axial, indexing="ij")
        expected = 4 * radial_mesh**2 + 3 * axial_mesh**2
        errors.append(np.max(np.abs(divergence(radius, axial, radial_mesh**3, axial_mesh**3) - expected)))
    np.testing.assert_allclose(np.array(errors[:-1]) / errors[1:], 4, rtol=1e-10)


@pytest.mark.parametrize("tau", [1.0, 1e-6])
def test_comparison_divergence_convergence(tau):
    parameters = ComparisonParameters()
    errors = []
    for radial_count in (33, 65, 129):
        radius = np.linspace(0, np.sqrt(tau) / 2, radial_count)
        axial = np.linspace(-0.12 * tau ** (0.5 - parameters.h), 0.12 * tau ** (0.5 - parameters.h), 2 * radial_count - 1)
        radial_mesh, axial_mesh = np.meshgrid(radius, axial, indexing="ij")
        radial_velocity, _swirl, axial_velocity = velocity(radial_mesh, axial_mesh, tau, parameters)
        result = divergence(radius, axial, radial_velocity, axial_velocity)
        radial_similarity, eta, scale = to_similarity(radial_mesh, axial_mesh, tau, parameters.h)
        _swirl, _axial, radial_coefficient = comparison_profiles(radial_similarity, eta, parameters)
        errors.append(float(np.max(np.abs(result)) / np.max(np.abs(radial_coefficient / scale))))
    assert np.all(np.log2(np.array(errors[:-1]) / errors[1:]) > 1.95), errors
    assert errors[-1] < 1e-5


@pytest.mark.parametrize("invalid", ["axis", "shape", "nonuniform", "nan", "negative"])
def test_invalid_grid_or_field(invalid):
    radius = np.linspace(0, 1, 5)
    axial = np.linspace(-1, 1, 5)
    radial_velocity = np.zeros((5, 5))
    axial_velocity = np.zeros((5, 5))
    if invalid == "axis":
        radial_velocity[0] = 1
    elif invalid == "shape":
        axial_velocity = axial_velocity[:-1]
    elif invalid == "nonuniform":
        radius[1] = 0.1
    elif invalid == "nan":
        axial_velocity[1, 1] = np.nan
    else:
        radius -= 1
    with pytest.raises(ValueError):
        divergence(radius, axial, radial_velocity, axial_velocity)