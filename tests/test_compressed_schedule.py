import numpy as np
import pytest

from nsblowup.compressed_not_theorem_admissible import CompressedNotTheoremAdmissibleSchedule, OVERRIDABLE
from nsblowup.relaxed_schedule import RelaxedSchedule


def test_unit_compression_exactly_reproduces_reference():
    reference = RelaxedSchedule()
    lengths = {stage.name: stage.length for stage in reference.stages if stage.name in OVERRIDABLE}
    compressed = CompressedNotTheoremAdmissibleSchedule(lengths=lengths)
    assert compressed.span == reference.span
    assert compressed.q_stop_length == reference.q_stop_length
    eta = np.linspace(-1, 1, 33)
    np.testing.assert_array_equal(compressed.pressure(eta), reference.pressure(eta))
    for original, modified in zip(reference.stages, compressed.stages):
        np.testing.assert_array_equal(original.log_swirl(original.length / 2, eta), modified.log_swirl(modified.length / 2, eta))
    assert all(not record["changed"] and not record["sacrificed"] for record in compressed.overrides)


@pytest.mark.parametrize("length", [0, -1, np.inf, np.nan])
def test_nonpositive_or_nonfinite_override_fails(length):
    with pytest.raises(ValueError, match="finite and positive"):
        CompressedNotTheoremAdmissibleSchedule(lengths={"intermediate_power": length})


def test_q_hold_cannot_be_overridden():
    with pytest.raises(ValueError, match="cannot be overridden"):
        CompressedNotTheoremAdmissibleSchedule(lengths={"q_stopping_hold": 1})


def test_aggressive_schedule_joins_pressure_derivatives_and_q():
    lengths = dict.fromkeys(OVERRIDABLE, 1.0)
    lengths.update(profile_interpolation=8.0, release_hold=2.0)
    schedule = CompressedNotTheoremAdmissibleSchedule(lengths=lengths)
    eta = np.linspace(-0.98, 0.98, 33)
    for left, right in zip(schedule.stages[:-1], schedule.stages[1:]):
        for order in (0, 1, 2):
            np.testing.assert_allclose(left.log_swirl(left.length, eta, order), right.log_swirl(0, eta, order), atol=1e-12)
    values = schedule.pressure(eta)
    tighter = CompressedNotTheoremAdmissibleSchedule(lengths=lengths, rtol=1e-12, atol=1e-14)
    np.testing.assert_allclose(values, tighter.pressure(eta), atol=1e-10, rtol=1e-11)
    errors = []
    for spacing in (0.004, 0.002, 0.001):
        upper, lower = schedule.pressure(eta + spacing)[0], schedule.pressure(eta - spacing)[0]
        numerical = np.stack([(upper - lower) / (2 * spacing), (upper - 2 * values[0] + lower) / spacing**2])
        errors.append(np.max(np.abs(numerical - values[1:]), axis=1))
    assert np.all(np.asarray(errors[:-1]) / np.asarray(errors[1:]) > 3.9)
    assert 0 < schedule.q_target < schedule.q_before_stop
    np.testing.assert_allclose(schedule.q_before_stop * np.exp(-(1 - schedule.parameters.h) * schedule.q_stop_length), schedule.q_target, rtol=1e-14)
    assert abs(schedule.q_terminal) < 1e-11
    assert schedule.q_stop_length != RelaxedSchedule().q_stop_length
    conditions = schedule.condition_status()
    assert conditions["conditional_q_matching"]
    assert not any(conditions[key] for key in ("reserved_supports_fit", "principal_axial_supports_fit", "principal_angular_supports_fit", "eta_slope_bound", "global_moments_verified"))


def test_sacrifices_and_supports_are_explicit():
    lengths = {"intermediate_power": 1, "axial_pulse_swirl_interval": 59,
               "angular_bump_interval_unbumped": 4, "profile_interpolation": 56, "release_hold": 2}
    schedule = CompressedNotTheoremAdmissibleSchedule(lengths=lengths)
    status = schedule.condition_status()
    assert status["principal_axial_supports_fit"] and status["principal_angular_supports_fit"] and status["eta_slope_bound"]
    assert not status["reserved_supports_fit"] and not status["paper_release_factors"]
    for record in schedule.overrides:
        assert record["ratio"] == record["modified_length"] / record["original_length"]
        assert record["sacrificed"] and record["not_checked"] and record["retained"]