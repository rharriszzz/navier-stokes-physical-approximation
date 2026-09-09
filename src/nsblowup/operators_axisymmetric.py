"""Second-order axisymmetric divergence on a physical (r,z) grid."""

import numpy as np


def divergence(radius, axial, radial_velocity, axial_velocity):
    """Compute divergence with regular-axis limit, including boundary points.

    Arrays have shape (len(radius), len(axial)); both coordinate axes must
    be uniform and increasing. Smooth Cartesian axisymmetry requires u_r=0
    at r=0 and even u_z there. No epsilon replaces a radius.
    """
    radius = np.asarray(radius, dtype=np.float64)
    axial = np.asarray(axial, dtype=np.float64)
    radial_velocity = np.asarray(radial_velocity, dtype=np.float64)
    axial_velocity = np.asarray(axial_velocity, dtype=np.float64)
    for coordinate in (radius, axial):
        if coordinate.ndim != 1 or coordinate.size < 3 or not np.all(np.isfinite(coordinate)):
            raise ValueError("coordinates must be finite 1D arrays with at least three points")
        spacing = np.diff(coordinate)
        if np.any(spacing <= 0) or not np.allclose(spacing, spacing[0], rtol=1e-10, atol=0):
            raise ValueError("coordinates must be strictly increasing and uniform")
    if radius[0] < 0:
        raise ValueError("radius must be nonnegative")
    for component in (radial_velocity, axial_velocity):
        if component.shape != (len(radius), len(axial)) or not np.all(np.isfinite(component)):
            raise ValueError("velocity components must be finite arrays on the (r,z) grid")
    if radius[0] == 0.0 and np.any(radial_velocity[0] != 0.0):
        raise ValueError("a regular axis requires u_r=0 at r=0")
    radial_derivative = np.gradient(radial_velocity, radius, axis=0, edge_order=2)
    axial_derivative = np.gradient(axial_velocity, axial, axis=1, edge_order=2)
    radial_quotient = np.zeros_like(radial_velocity)
    np.divide(radial_velocity, radius[:, None], out=radial_quotient, where=radius[:, None] != 0)
    if radius[0] == 0.0:
        radial_quotient[0] = radial_derivative[0]
    return radial_derivative + radial_quotient + axial_derivative