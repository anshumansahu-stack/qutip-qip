import numpy as np
from qutip import Qobj
import qutip.control.pulseoptim as cpo

# ─────────────────────────────────────────
# CORE OPTIMIZER
# ─────────────────────────────────────────


def run_grape(U_targ, n_restarts=20, n_ts=100, evo_t=20.0):
    """
    Runs dual quadrature GRAPE optimization for a given target unitary.
    Returns the best result across n_restarts random initializations.
    """
    H_drift = Qobj([[0, 0], [0, 0]])
    sx = Qobj([[0, 1], [1, 0]])
    sy = Qobj([[0, -1j], [1j, 0]])
    H_ctrls = [sx, sy]
    U_0 = Qobj(np.eye(2))

    best_result = None
    best_fid_err = 1.0

    for i in range(n_restarts):
        result = cpo.optimize_pulse_unitary(
            H_drift,
            H_ctrls,
            U_0,
            U_targ,
            num_tslots=n_ts,
            evo_time=evo_t,
            fid_err_targ=1e-5,
            max_iter=1000,
            init_pulse_type="RND",
            optim_method="FMIN_BFGS",
            gen_stats=False,
        )
        if result.fid_err < best_fid_err:
            best_fid_err = result.fid_err
            best_result = result

    return best_result


# ─────────────────────────────────────────
# TEST CASES
# ─────────────────────────────────────────


def test_NOT_gate():
    print("\n[TEST 1] NOT Gate (X Gate)")
    U_targ = Qobj([[0, 1], [1, 0]])
    result = run_grape(U_targ)
    fid = 1.0 - result.fid_err
    print(f"  Fidelity Error : {result.fid_err:.2e}")
    print(f"  Fidelity       : {fid:.5%}")
    assert (
        result.fid_err < 1e-4
    ), f"FAILED — fidelity error too high: {result.fid_err}"
    print("  PASSED ✓")


def test_identity_gate():
    print("\n[TEST 2] Identity Gate")
    U_targ = Qobj([[1, 0], [0, 1]])
    result = run_grape(U_targ)
    fid = 1.0 - result.fid_err
    print(f"  Fidelity Error : {result.fid_err:.2e}")
    print(f"  Fidelity       : {fid:.5%}")
    assert (
        result.fid_err < 1e-4
    ), f"FAILED — fidelity error too high: {result.fid_err}"
    print("  PASSED ✓")


def test_hadamard_gate():
    print("\n[TEST 3] Hadamard Gate")
    U_targ = Qobj([[1, 1], [1, -1]]) / np.sqrt(2)
    result = run_grape(U_targ)
    fid = 1.0 - result.fid_err
    print(f"  Fidelity Error : {result.fid_err:.2e}")
    print(f"  Fidelity       : {fid:.5%}")
    assert (
        result.fid_err < 1e-4
    ), f"FAILED — fidelity error too high: {result.fid_err}"
    print("  PASSED ✓")


def test_RX_gate():
    print("\n[TEST 4] RX(π/2) Gate")
    theta = np.pi / 2
    U_targ = Qobj(
        [
            [np.cos(theta / 2), -1j * np.sin(theta / 2)],
            [-1j * np.sin(theta / 2), np.cos(theta / 2)],
        ]
    )
    result = run_grape(U_targ)
    fid = 1.0 - result.fid_err
    print(f"  Fidelity Error : {result.fid_err:.2e}")
    print(f"  Fidelity       : {fid:.5%}")
    assert (
        result.fid_err < 1e-4
    ), f"FAILED — fidelity error too high: {result.fid_err}"
    print("  PASSED ✓")


def test_RY_gate():
    print("\n[TEST 5] RY(π/4) Gate")
    theta = np.pi / 4
    U_targ = Qobj(
        [
            [np.cos(theta / 2), -np.sin(theta / 2)],
            [np.sin(theta / 2), np.cos(theta / 2)],
        ]
    )
    result = run_grape(U_targ)
    fid = 1.0 - result.fid_err
    print(f"  Fidelity Error : {result.fid_err:.2e}")
    print(f"  Fidelity       : {fid:.5%}")
    assert (
        result.fid_err < 1e-4
    ), f"FAILED — fidelity error too high: {result.fid_err}"
    print("  PASSED ✓")


def test_random_unitary():
    print("\n[TEST 6] Random 2x2 Unitary")
    from scipy.stats import unitary_group

    U_targ = Qobj(unitary_group.rvs(2))
    result = run_grape(U_targ)
    fid = 1.0 - result.fid_err
    print(f"  Fidelity Error : {result.fid_err:.2e}")
    print(f"  Fidelity       : {fid:.5%}")
    assert (
        result.fid_err < 1e-4
    ), f"FAILED — fidelity error too high: {result.fid_err}"
    print("  PASSED ✓")


# ─────────────────────────────────────────
# STRESS TEST
# ─────────────────────────────────────────


def stress_test(n_trials=50):
    from scipy.stats import unitary_group

    print(f"\n--- STRESS TEST: {n_trials} RANDOM UNITARIES ---")

    passed = 0
    failed = 0
    fidelities = []

    for i in range(n_trials):
        U_targ = Qobj(unitary_group.rvs(2))
        result = run_grape(U_targ, n_restarts=10)
        fid = 1.0 - result.fid_err
        fidelities.append(fid)

        if result.fid_err < 1e-4:
            passed += 1
        else:
            failed += 1
            print(
                f"  Trial {i+1:02d}: FAILED — Fidelity Error = {result.fid_err:.2e}"
            )

    print(
        f"\nResults        : {passed}/{n_trials} passed (threshold: fid_err < 1e-4)"
    )
    print(f"Mean Fidelity  : {np.mean(fidelities):.5%}")
    print(f"Min  Fidelity  : {np.min(fidelities):.5%}")
    print(f"Max  Fidelity  : {np.max(fidelities):.5%}")
    return passed, fidelities


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("IMP_11: DUAL QUADRATURE GRAPE — TEST SUITE")
    print("=" * 50)

    test_NOT_gate()
    test_identity_gate()
    test_hadamard_gate()
    test_RX_gate()
    test_RY_gate()
    test_random_unitary()

    stress_test(n_trials=50)

"""
OUTPUT:
==================================================
IMP_11: DUAL QUADRATURE GRAPE — TEST SUITE
==================================================

[TEST 1] NOT Gate (X Gate)
  Fidelity Error : 2.73e-08
  Fidelity       : 100.00000%
  PASSED ✓

[TEST 2] Identity Gate
  Fidelity Error : 2.04e-10
  Fidelity       : 100.00000%
  PASSED ✓

[TEST 3] Hadamard Gate
  Fidelity Error : 5.92e-10
  Fidelity       : 100.00000%
  PASSED ✓

[TEST 4] RX(π/2) Gate
  Fidelity Error : 1.29e-08
  Fidelity       : 100.00000%
  PASSED ✓

[TEST 5] RY(π/4) Gate
  Fidelity Error : 4.62e-09
  Fidelity       : 100.00000%
  PASSED ✓

[TEST 6] Random 2x2 Unitary
  Fidelity Error : 4.78e-12
  Fidelity       : 100.00000%
  PASSED ✓

--- STRESS TEST: 50 RANDOM UNITARIES ---

Results        : 50/50 passed (threshold: fid_err < 1e-4)
Mean Fidelity  : 99.99999%
Min  Fidelity  : 99.99990%
Max  Fidelity  : 100.00000%
"""
