"""Published Appendix B comparison, NOT the solved nonlinear core profile."""

from dataclasses import dataclass

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import hyp0f1

from nsblowup.coordinates import to_similarity, validate_h


@dataclass(frozen=True)
class ComparisonParameters:
    h: float = 0.005
    radial_parameter: float = 32.0
    sigma: float = 0.2
    axial_offset: float = 0.025
    swirl_peak: float = 1.0

    def __post_init__(self):
        validate_h(self.h)
        if not np.isfinite(self.radial_parameter) or self.radial_parameter < 1:
            raise ValueError("Lambda must be finite and at least one")
        if not np.isfinite(self.sigma) or self.sigma <= 0:
            raise ValueError("sigma must be finite and positive")
        if not np.isfinite(self.axial_offset) or not 0 < self.axial_offset <= 0.05:
            raise ValueError("j0 must be in (0, 0.05]")
        if not np.isfinite(self.swirl_peak) or not 0 < self.swirl_peak <= 1:
            raise ValueError("normalized real-axis swirl peak must be in (0, 1]")


def comparison_function(argument):
    """Evaluate (B.11) as 0F1(;2;-argument/2), including its axis limit."""
    argument = np.asarray(argument, dtype=np.float64)
    if np.any(~np.isfinite(argument)) or np.any((argument < 0) | (argument > 4.1)):
        raise ValueError("the comparison is restricted to 0 <= argument <= 4.1")
    return hyp0f1(2.0, -argument / 2.0)


def _axis_transport(eta, parameters):
    return (0.5 - parameters.h) * eta + (1.0 - eta**2) * (
        4.0 * eta + parameters.axial_offset
    )


def _normalized_axis_swirl(eta, parameters):
    root = brentq(lambda axial: _axis_transport(axial, parameters), -1.0, 0.0)

    def logarithmic_derivative(axial):
        transport = _axis_transport(axial, parameters)
        denominator = 1.0 - 2.0 * parameters.h * axial**2
        return -denominator * transport / (transport**2 + parameters.sigma**2)

    unique_eta, inverse = np.unique(eta, return_inverse=True)
    logarithms = np.array([
        parameters.radial_parameter
        * quad(logarithmic_derivative, root, axial, epsabs=1e-12, epsrel=1e-12)[0]
        for axial in unique_eta
    ])
    return (parameters.swirl_peak * np.exp(logarithms))[inverse].reshape(eta.shape)


def comparison_profiles(radial_similarity, eta, parameters):
    """Return (E, U, V0/X) for Phi=f0(Lambda X chi), U=U_star.

    See (B.1)-(B.3), (B.11)-(B.13), and (4.7). The omitted nonlinear
    corrections mean that zero leading momentum residual is NOT asserted.
    """
    radial_similarity, eta = np.broadcast_arrays(
        np.asarray(radial_similarity, dtype=np.float64),
        np.asarray(eta, dtype=np.float64),
    )
    scaled_radius = parameters.radial_parameter * radial_similarity
    if np.any(~np.isfinite(scaled_radius)) or np.any((scaled_radius < 0) | (scaled_radius > 4.1)):
        raise ValueError("comparison domain requires 0 <= Lambda X <= 4.1")
    if np.any(~np.isfinite(eta)) or np.any(np.abs(eta) >= 1):
        raise ValueError("comparison domain requires |eta| < 1")
    transport = _axis_transport(eta, parameters)
    chi = transport**2 / (transport**2 + parameters.sigma**2)
    axis_swirl = _normalized_axis_swirl(eta, parameters)
    swirl = np.sqrt(2.0 * radial_similarity) * axis_swirl * comparison_function(scaled_radius * chi)
    axial = 4.0 * eta + parameters.axial_offset
    radial_coefficient = (
        2.0 * (0.5 + parameters.h) * eta * axial - 4.0 * (1.0 - eta**2)
    ) / (1.0 - 2.0 * parameters.h * eta**2)
    return swirl, axial, radial_coefficient


def velocity(radius, axial, tau, parameters):
    """Return float64 cylindrical (u_r, u_theta, u_z), smooth at r=0."""
    radial_similarity, eta, scale = to_similarity(radius, axial, tau, parameters.h)
    swirl, axial_profile, radial_coefficient = comparison_profiles(
        radial_similarity, eta, parameters
    )
    amplitude = scale ** (-0.5 - parameters.h)
    return (
        radial_coefficient * np.asarray(radius, dtype=np.float64) / (2.0 * scale),
        amplitude * swirl,
        amplitude * axial_profile,
    )