# IMP_8_Circuit_Builder.py
# Builds QubitCircuit from CSD decomposition angles
# Pattern: RY(θ₁) → CNOT → RY(θ₂)
# Tests: Original, Zero, Pi, Pi/2, Asymmetric, Negative, Stress(100x)
# Status: ALL TESTS PASSING ✓
from qutip_qip.circuit import QubitCircuit
from qutip_qip.operations import Gate
import numpy as np

def verify_circuit(qc, test_name, expected_gates, expected_angles):
    print(f"\n--- {test_name} ---")
    gates = qc.gates
    
    # Check gate count
    gate_count_correct = len(gates) == len(expected_gates)
    print(f"Gate count: {len(gates)} (expected {len(expected_gates)}) {'✓' if gate_count_correct else '✗'}")
    
    # Check gate names
    actual_names = [g.name for g in gates]
    names_correct = actual_names == expected_gates
    print(f"Gate sequence: {actual_names} {'✓' if names_correct else '✗'}")
    
    # Check angles
    actual_angles = [g.arg_value for g in gates]
    angles_correct = True
    for i, (actual, expected) in enumerate(zip(actual_angles, expected_angles)):
        if expected is None:
            if actual is not None:
                angles_correct = False
        else:
            if not np.isclose(actual, expected, atol=1e-6):
                angles_correct = False
    print(f"Angles correct: {'✓' if angles_correct else '✗'}")
    
    overall = gate_count_correct and names_correct and angles_correct
    print(f"{'✓ PASS' if overall else '✗ FAIL'}")
    return overall

def test_circuit_builder(thetas):
    qc = QubitCircuit(2)
    # This is how Tier 2 will 'talk' to the compiler
    qc.add_gate("RY", targets=[1], arg_value=thetas[0])
    qc.add_gate("CNOT", controls=[0], targets=[1])
    qc.add_gate("RY", targets=[1], arg_value=thetas[1])
    return qc

# Use your angles from yesterday
my_thetas = [0.6920, 1.2768]
circuit = test_circuit_builder(my_thetas)
print("Circuit successfully built from CSD angles!")
for gate in circuit.gates:
    print(f"Gate: {gate.name}, Targets: {gate.targets}, Angle: {gate.arg_value}")
'''
**Output**
Circuit successfully built from CSD angles!
Gate: RY, Targets: [1], Angle: 0.692
Gate: CNOT, Targets: [1], Angle: None
Gate: RY, Targets: [1], Angle: 1.2768
'''

# ─────────────────────────────────────────
# TEST 1 — Original angles from CSD
# ─────────────────────────────────────────
thetas = [0.6920, 1.2768]
qc = test_circuit_builder(thetas)
verify_circuit(qc, "TEST 1: Original CSD Angles",
    expected_gates=["RY", "CNOT", "RY"],
    expected_angles=[0.6920, None, 1.2768])

# ─────────────────────────────────────────
# TEST 2 — Zero angles (Identity case)
# ─────────────────────────────────────────
thetas = [0.0, 0.0]
qc = test_circuit_builder(thetas)
verify_circuit(qc, "TEST 2: Zero Angles (Identity)",
    expected_gates=["RY", "CNOT", "RY"],
    expected_angles=[0.0, None, 0.0])

# ─────────────────────────────────────────
# TEST 3 — Pi angles (Maximum rotation)
# ─────────────────────────────────────────
thetas = [np.pi, np.pi]
qc = test_circuit_builder(thetas)
verify_circuit(qc, "TEST 3: Pi Angles (Maximum rotation)",
    expected_gates=["RY", "CNOT", "RY"],
    expected_angles=[np.pi, None, np.pi])

# ─────────────────────────────────────────
# TEST 4 — Pi/2 angles
# ─────────────────────────────────────────
thetas = [np.pi/2, np.pi/2]
qc = test_circuit_builder(thetas)
verify_circuit(qc, "TEST 4: Pi/2 Angles",
    expected_gates=["RY", "CNOT", "RY"],
    expected_angles=[np.pi/2, None, np.pi/2])

# ─────────────────────────────────────────
# TEST 5 — Asymmetric angles
# ─────────────────────────────────────────
thetas = [0.3947, 1.4627]
qc = test_circuit_builder(thetas)
verify_circuit(qc, "TEST 5: Asymmetric Angles (Random unitary)",
    expected_gates=["RY", "CNOT", "RY"],
    expected_angles=[0.3947, None, 1.4627])

# ─────────────────────────────────────────
# TEST 6 — Negative angles
# ─────────────────────────────────────────
thetas = [-np.pi/4, -np.pi/3]
qc = test_circuit_builder(thetas)
verify_circuit(qc, "TEST 6: Negative Angles",
    expected_gates=["RY", "CNOT", "RY"],
    expected_angles=[-np.pi/4, None, -np.pi/3])

# ─────────────────────────────────────────
# STRESS TEST — 100 random angle pairs
# ─────────────────────────────────────────
print("\n--- STRESS TEST: 100 Random Angle Pairs ---")
passed = 0
failed = 0

np.random.seed(42)
for i in range(100):
    thetas = np.random.uniform(-np.pi, np.pi, 2)
    try:
        qc = test_circuit_builder(thetas)
        gates = qc.gates
        
        # Verify structure
        names_correct = [g.name for g in gates] == ["RY", "CNOT", "RY"]
        angles_correct = (
            np.isclose(gates[0].arg_value, thetas[0], atol=1e-10) and
            gates[1].arg_value is None and
            np.isclose(gates[2].arg_value, thetas[1], atol=1e-10)
        )
        
        if names_correct and angles_correct:
            passed += 1
        else:
            failed += 1
            print(f"✗ FAIL — Iteration {i}")
    except Exception as e:
        failed += 1
        print(f"✗ ERROR — Iteration {i}: {e}")

print(f"Passed: {passed}/100")
print(f"Failed: {failed}/100")
print("All circuits built correctly!" if failed == 0 else "Some failures detected!")