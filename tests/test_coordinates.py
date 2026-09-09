import numpy as np
import pytest

from nsblowup.coordinates import to_physical, to_similarity


@pytest.mark.parametrize("tau", [1.0, 1e-4, 1e-12])
@pytest.mark.parametrize("h", [0.001, 0.005, 0.009])
def test_round_trip_and_implicit_identity(tau, h):
    radial = np.linspace(0, 0.1, 11)[:, None]
    eta = np.array([-0.99, -0.5, 0.0, 0.3, 0.99])[None, :]
    radius, axial, expected_scale = to_physical(radial, eta, tau, h)
    actual_radial, actual_eta, scale = to_similarity(radius, axial, tau, h)
    np.testing.assert_allclose(actual_radial, np.broadcast_to(radial, radius.shape), rtol=2e-14)
    np.testing.assert_allclose(actual_eta, np.broadcast_to(eta, radius.shape), atol=2e-15)
    np.testing.assert_allclose(scale, expected_scale, rtol=2e-14)
    np.testing.assert_allclose(scale - axial**2 * scale ** (2 * h), tau, rtol=2e-13)
    assert scale.dtype == np.float64


def test_midplane_and_physical_round_trip():
    radial, eta, scale = to_similarity(2.0, 0.0, 0.25, 0.005)
    assert radial == pytest.approx(8.0)
    assert eta == 0.0
    assert scale == pytest.approx(0.25)
    radius, axial, _scale = to_physical(radial, eta, 0.25, 0.005)
    assert radius == pytest.approx(2.0)
    assert axial == 0.0


@pytest.mark.parametrize("tau", [0.0, -1.0, np.nan, np.inf])
def test_invalid_time(tau):
    with pytest.raises(ValueError):
        to_similarity(0.0, 0.0, tau, 0.005)


@pytest.mark.parametrize("h", [0.0, 0.01, np.nan])
def test_invalid_exponent(h):
    with pytest.raises(ValueError):
        to_physical(0.0, 0.0, 1.0, h)


@pytest.mark.parametrize("radial,eta", [(-1, 0), (0, 1), (0, -1), (np.inf, 0), (0, np.nan)])
def test_invalid_similarity_domain(radial, eta):
    with pytest.raises(ValueError):
        to_physical(radial, eta, 1.0, 0.005)