"""Length-only modified Appendix A schedule; NOT theorem-admissible.

Source roles and sacrificed estimates: notes/compression-audit.md.
"""

import numpy as np

from nsblowup.relaxed_schedule import RelaxedParameters, RelaxedSchedule


OVERRIDABLE = {
    "intermediate_power": ("A.9, A.14, A.27; pp129,131,135", "lambda^30 amplitude and transient moment/Q margins"),
    "axial_pulse_swirl_interval": ("A.15, A.19-A.20, A.28-A.30; pp131,133,135-136", "original pulse integral to 13 and exponentially small end corrections"),
    "angular_bump_interval_unbumped": ("A.11, A.1-A.3; pp127,130-132", "lambda^28 moment discrepancy and small pressure-preserving angular correction"),
    "profile_interpolation": ("A.10; pp130,136", "original interpolation duration (slope bound assessed separately)"),
    "release_hold": ("A.17-A.18; pp132,137", "h^8 and h^6 suppression and h-uniform stress/moment estimates"),
}


class CompressedNotTheoremAdmissibleSchedule(RelaxedSchedule):
    """Reuse the reference formulas while explicitly overriding selected lengths."""

    def __init__(self, parameters=None, lengths=None, rtol=1e-10, atol=1e-12):
        self.lengths = dict(lengths or {})
        unknown = self.lengths.keys() - OVERRIDABLE.keys()
        if unknown:
            raise ValueError(f"length cannot be overridden: {sorted(unknown)}")
        if any(not np.isfinite(value) or value <= 0 for value in self.lengths.values()):
            raise ValueError("overridden stage lengths must be finite and positive")
        self.overrides = []
        super().__init__(parameters or RelaxedParameters(), rtol, atol)

    def _add(self, name, length, exponent, slope_start, slope_end=None, kind="constant"):
        modified = float(self.lengths.get(name, length))
        stage = super()._add(name, modified, exponent, slope_start, slope_end, kind)
        if name in self.lengths:
            changed = bool(modified != length)
            retained = ["original local swirl and slope formulas", "positive finite length", "flat stage joins"]
            sacrificed = []
            if changed:
                sacrificed.append(OVERRIDABLE[name][1])
            support = self._condition(name, modified)
            if support is not None:
                description, satisfied = support
                if satisfied:
                    retained.append(description)
                else:
                    sacrificed.append(description)
            self.overrides.append({
                "stage": name, "source": OVERRIDABLE[name][0], "original_length": float(length),
                "modified_length": modified, "ratio": modified / length, "changed": changed,
                "retained": retained, "sacrificed": sacrificed,
                "not_checked": ["actual moment correction coefficients and identities", "stress cone inequalities",
                                "matching to a regular inner core", "later heat/background/phase corrections"],
            })
        return stage

    def _condition(self, name, length):
        if name == "intermediate_power":
            return "four paper-positioned reserved support patches fit", length > 25
        if name == "axial_pulse_swirl_interval":
            return "main pulse and separated width-.3 axial bump supports fit", length > 11 / self.parameters.outer_decay + 3.15
        if name == "angular_bump_interval_unbumped":
            return "two width-.3 angular bump supports fit", length > 3.15
        if name == "profile_interpolation":
            return "A.10 interpolation slope bound", length >= 80 * np.log(2)
        return None

    def condition_status(self):
        lengths = {stage.name: stage.length for stage in self.stages}
        conditions = {
            "reserved_supports_fit": lengths["intermediate_power"] > 25,
            "principal_axial_supports_fit": lengths["axial_pulse_swirl_interval"] > 11 / self.parameters.outer_decay + 3.15,
            "principal_angular_supports_fit": lengths["angular_bump_interval_unbumped"] > 3.15,
            "eta_slope_bound": lengths["profile_interpolation"] >= 80 * np.log(2),
            "paper_release_factors": lengths["release_hold"] == 4 * np.log(1 / self.parameters.h),
            "conditional_q_matching": self.q_stop_length > 0 and abs(self.q_terminal) < 1e-10,
            "global_moments_verified": False,
            "stress_verified": False,
            "theorem_admissible": False,
        }
        return {name: bool(value) for name, value in conditions.items()}