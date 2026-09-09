"""Similarity geometry from paper (3.2), (4.1); see notes/equation-map.md."""

import numpy as np


def validate_h(h):
    if not np.isfinite(h) or not 0.0 < h < 0.01:
        raise ValueError("h must be finite and in (0, 0.01)")


def _validate_tau(tau):
    if not np.isfinite(tau) or tau <= 0.0:
        raise ValueError("tau must be finite and positive")


def to_physical(radial_similarity, eta, tau, h):
    """Return (r, z, q) on a fixed positive-tau slice; inputs broadcast."""
    validate_h(h)
    _validate_tau(tau)
    radial_similarity, eta = np.broadcast_arrays(
        np.asarray(radial_similarity, dtype=np.float64),
        np.asarray(eta, dtype=np.float64),
    )
    if np.any(~np.isfinite(radial_similarity)) or np.any(radial_similarity < 0):
        raise ValueError("X must be finite and nonnegative")
    if np.any(~np.isfinite(eta)) or np.any(np.abs(eta) >= 1):
        raise ValueError("eta must be finite and strictly between -1 and 1")
    scale = tau / ((1.0 - eta) * (1.0 + eta))
    return np.sqrt(2.0 * radial_similarity * scale), scale ** (0.5 - h) * eta, scale


def to_similarity(radius, axial, tau, h):
    """Return (X, eta, q), solving a scaled monotone equation for q."""
    validate_h(h)
    _validate_tau(tau)
    radius, axial = np.broadcast_arrays(
        np.asarray(radius, dtype=np.float64), np.asarray(axial, dtype=np.float64)
    )
    if np.any(~np.isfinite(radius)) or np.any(radius < 0):
        raise ValueError("r must be finite and nonnegative")
    if np.any(~np.isfinite(axial)):
        raise ValueError("z must be finite")
    axial_scale = np.abs(axial) ** (1.0 / (0.5 - h))
    reference = np.maximum(tau, axial_scale)
    coefficient = (axial_scale / reference) ** (1.0 - 2.0 * h)
    scaled_tau = tau / reference
    lower = np.maximum(scaled_tau, axial_scale / reference)
    upper = np.full_like(lower, 3.0)
    for _iteration in range(56):
        middle = (lower + upper) / 2.0
        residual = middle - coefficient * middle ** (2.0 * h) - scaled_tau
        lower = np.where(residual < 0, middle, lower)
        upper = np.where(residual >= 0, middle, upper)
    scale = reference * ((lower + upper) / 2.0)
    eta = axial / scale ** (0.5 - h)
    return radius**2 / (2.0 * scale), eta, scale