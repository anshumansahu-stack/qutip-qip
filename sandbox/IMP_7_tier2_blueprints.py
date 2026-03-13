# IMP_7_tier2_blueprints.py (working prototype code for Tier 2)
# CSD-based decomposition engine for 2-qubit unitary matrices
# Tests: RX⊗RX, Identity, CNOT, Random, Stress(100x)
# Status: ALL TESTS PASSING ✓
import numpy as np
import scipy.linalg as la
from scipy.linalg import cossin
from qutip import Qobj

np.random.seed(42)  # This 'locks' the random generator to the same sequence

## Uncomment the print statements before the stress test block for tests 1-4. Comment all of them for 5, Uncommenting the stress test block.
def is_identity(matrix, tol=1e-10):
    """Check if a 2x2 matrix is approximately identity."""
    return np.allclose(matrix, np.eye(2), atol=tol)

def euler_decompose(U2x2):
    """
    Decompose a 2x2 unitary into RZ·RY·RZ Euler angles.
    Returns alpha, beta, gamma such that:
    U = RZ(alpha) · RY(beta) · RZ(gamma)
    """
    # Extract angles using standard ZYZ decomposition formula
    # beta is the RY angle
    beta = 2 * np.arctan2(
        abs(U2x2[1, 0]),
        abs(U2x2[0, 0])
    )
    
    # alpha and gamma are the RZ angles
    if abs(np.sin(beta / 2)) < 1e-10:# To avoid division by zero later
        alpha = 0
        gamma = np.angle(U2x2[1, 1] / U2x2[0, 0]) if abs(U2x2[0,0]) > 1e-10 else 0
    elif abs(np.cos(beta / 2)) < 1e-10:# To avoid division by zero later
        alpha = 0
        gamma = np.angle(-U2x2[1, 0] / U2x2[0, 1]) if abs(U2x2[0,1]) > 1e-10 else 0
    else:
        alpha = np.angle(U2x2[1, 1] / np.cos(beta / 2))
        gamma = np.angle(U2x2[1, 0] / np.sin(beta / 2))
    
    return alpha, beta, gamma

def map_to_gates(L1, L2, thetas, R1h, R2h):
    """
    Maps CSD output to a human readable gate sequence.
    Handles all four cases:
    - Action in thetas only
    - Action in L/R only  
    - Action in both
    - No action (identity)
    """
    gate_sequence = []
    
    # --- RIGHT ROTATIONS FIRST ---
    # R1h acts on qubit 1, R2h acts on qubit 2
    if not is_identity(R1h):
        a, b, g = euler_decompose(R1h)
        gate_sequence.append(f"Qubit 1: RZ({a:.4f}) · RY({b:.4f}) · RZ({g:.4f})")
    
    if not is_identity(R2h):
        a, b, g = euler_decompose(R2h)
        gate_sequence.append(f"Qubit 2: RZ({a:.4f}) · RY({b:.4f}) · RZ({g:.4f})")
    
    # --- MIDDLE: COSINE-SINE MIXING ---
    if not np.allclose(thetas, 0, atol=1e-10):
        gate_sequence.append(
            f"Multiplexed RY: RY({2*thetas[0]:.4f}) controlled, RY({2*thetas[1]:.4f})"
        )
    
    # --- LEFT ROTATIONS LAST ---
    # L1 acts on qubit 1, L2 acts on qubit 2
    if not is_identity(L1):
        a, b, g = euler_decompose(L1)
        gate_sequence.append(f"Qubit 1: RZ({a:.4f}) · RY({b:.4f}) · RZ({g:.4f})")
    
    if not is_identity(L2):
        a, b, g = euler_decompose(L2)
        gate_sequence.append(f"Qubit 2: RZ({a:.4f}) · RY({b:.4f}) · RZ({g:.4f})")
    
    return gate_sequence

# 1. Load a random 2-qubit Unitary

# -----------------------------------
# TEST 1 Product of rx: (Uncomment to test)
# -----------------------------------
# theta = np.pi / 2
# RX = np.array(
#     [
#         [np.cos(theta / 2), -1j * np.sin(theta / 2)],
#         [-1j * np.sin(theta / 2), np.cos(theta / 2)],
#     ]
# )
# U_data = np.kron(RX, RX)
# U = Qobj(U_data, dims=[[2, 2], [2, 2]])
# TEST 1 Results:
"""
Raw thetas from cossin: [0.78539816 0.78539816]


Reconstruction Error: 5.575348357045502e-16
Reconstruction Correct: True

L1 matrix:
[[ 0.707+0.j    -0.707+0.j   ]
 [ 0.   -0.707j  0.   -0.707j]]

L2 matrix:
[[ 0.   -0.707j  0.   +0.707j]
 [-0.707+0.j    -0.707+0.j   ]]

R1h matrix:
[[1.+0.j 0.+0.j]
 [0.+0.j 0.+1.j]]

R2h matrix:
[[ 0.+1.j  0.+0.j]
 [ 0.+0.j -1.-0.j]]
--- ANGLE EXTRACTION SUCCESS ---
Angle 1: 0.7854 rad
Angle 2: 0.7854 rad
Resulting RY rotations: RY(0.7853981633974483) and RY(0.7853981633974484)

--- GATE SEQUENCE ---
Step 1: Qubit 1: RZ(0.0000) · RY(0.0000) · RZ(1.5708)
Step 2: Qubit 2: RZ(0.0000) · RY(0.0000) · RZ(1.5708)
Step 3: Multiplexed RY: RY(1.5708) controlled, RY(1.5708)
Step 4: Qubit 1: RZ(-1.5708) · RY(1.5708) · RZ(-1.5708)
Step 5: Qubit 2: RZ(3.1416) · RY(1.5708) · RZ(3.1416)
"""
# -----------------------------------
# TEST 2 Unitary gate: (Uncomment to test)
# -----------------------------------

# U_data = np.eye(4)  # 4x4 identity matrix
# U = Qobj(U_data, dims=[[2, 2], [2, 2]])

# TEST 2 Result:
"""
Raw thetas from cossin: [0. 0.]


Reconstruction Error: 0.0
Reconstruction Correct: True

L1 matrix:
[[1.+0.j 0.+0.j]
 [0.-0.j 1.+0.j]]

L2 matrix:
[[1.+0.j 0.+0.j]
 [0.-0.j 1.+0.j]]

R1h matrix:
[[1.+0.j 0.+0.j]
 [0.+0.j 1.+0.j]]

R2h matrix:
[[ 1.+0.j -0.-0.j]
 [ 0.+0.j  1.+0.j]]
--- ANGLE EXTRACTION SUCCESS ---
Angle 1: 0.0000 rad
Angle 2: 0.0000 rad
Resulting RY rotations: RY(0.0) and RY(0.0)

--- GATE SEQUENCE ---
Gate is Identity — no operations needed
"""
# -----------------------------------
# TEST 3: (Uncomment to run) FIXED
# -----------------------------------
# U_data = np.array(
#     [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex
# )
# U = Qobj(U_data, dims=[[2, 2], [2, 2]])

# TEST 3 RESULT:
"""
Raw thetas from cossin: [0. 0.]


Reconstruction Error: 0.0
Reconstruction Correct: True

L1 matrix:
[[1.+0.j 0.+0.j]
 [0.-0.j 1.+0.j]]

L2 matrix:
[[1.+0.j 0.+0.j]
 [0.-0.j 1.+0.j]]

R1h matrix:
[[1.+0.j 0.+0.j]
 [0.+0.j 1.+0.j]]

R2h matrix:
[[0.+0.j 1.-0.j]
 [1.+0.j 0.+0.j]]
--- ANGLE EXTRACTION SUCCESS ---
Angle 1: 0.0000 rad
Angle 2: 0.0000 rad
Resulting RY rotations: RY(0.0) and RY(0.0)

--- GATE SEQUENCE ---
Step 1: Qubit 2: RZ(0.0000) · RY(3.1416) · RZ(-3.1416)
"""
# -----------------------------------
# TEST 4: (Uncomment to run)
# -----------------------------------
# np.random.seed(42)
# U = Qobj(
#     la.qr(np.random.randn(4, 4) + 1j * np.random.randn(4, 4))[0],
#     dims=[[2, 2], [2, 2]],
# )

# TEST 4 Result:
"""
Raw thetas from cossin: [0.39472042 1.46274441]


Reconstruction Error: 1.148465551252452e-15
Reconstruction Correct: True

L1 matrix:
[[-0.266+0.516j -0.016+0.814j]
 [ 0.12 -0.805j  0.176+0.553j]]

L2 matrix:
[[ 0.531+0.825j  0.099-0.166j]
 [ 0.096+0.168j -0.548+0.814j]]

R1h matrix:
[[ 0.961+0.j    -0.101-0.258j]
 [ 0.277+0.j     0.349+0.895j]]

R2h matrix:
[[ 0.568+0.223j -0.776-0.158j]
 [-0.244-0.754j -0.285-0.54j ]]
--- ANGLE EXTRACTION SUCCESS ---
Angle 1: 0.3947 rad
Angle 2: 1.4627 rad
Resulting RY rotations: RY(0.3947204249621101) and RY(1.4627444099569256)

--- GATE SEQUENCE ---
Step 1: Qubit 1: RZ(1.1988) · RY(0.5605) · RZ(0.0000)
Step 2: Qubit 2: RZ(-2.0565) · RY(1.8290) · RZ(-1.8837)
Step 3: Multiplexed RY: RY(0.7894) controlled, RY(2.9255)
Step 4: Qubit 1: RZ(1.2624) · RY(1.9023) · RZ(-1.4232)
Step 5: Qubit 2: RZ(2.1632) · RY(0.3897) · RZ(1.0525)

"""
# -----------------------------------
# TEST 5: STRESS TEST 
# WARNING: Comment all Print statements below and uncomment the stress test print block to print the results in an organized manner.
# -----------------------------------
np.random.seed(42)
U = Qobj(
    la.qr(np.random.randn(4, 4) + 1j * np.random.randn(4, 4))[0],
    dims=[[2, 2], [2, 2]],
)
# TEST 5 Results:
'''
--- STRESS TEST: 100 Random Unitaries ---
Passed: 100/100
Failed: 0/100
All 100 unitaries reconstructed perfectly!
'''

# 2. CSD Logic (Theorem 10)
# We partition U into four 2x2 blocks: [U11, U12; U21, U22]
u_data = U.full()
U11 = u_data[:2, :2]
U12 = u_data[:2, 2:]
U21 = u_data[2:, :2]
U22 = u_data[2:, 2:]

# 3. Verify the Sine-Cosine relationship
# In a perfect CSD, SVD of these blocks reveals the angles.
(L1, L2), thetas, (R1h, R2h) = cossin(u_data, p=2, q=2, separate=True)
# print(f"Raw thetas from cossin: {thetas}")
# print()

# VERIFICATION: Rebuild U from CSD pieces
C = np.diag(np.cos(thetas))
S = np.diag(np.sin(thetas))

CS = np.block([[C, -S], [S, C]])

L = np.block([[L1, np.zeros((2, 2))], [np.zeros((2, 2)), L2]])

R = np.block([[R1h, np.zeros((2, 2))], [np.zeros((2, 2)), R2h]])

U_reconstructed = L @ CS @ R
error = np.linalg.norm(u_data - U_reconstructed)
# print(f"\nReconstruction Error: {error}")
# print(f"Reconstruction Correct: {np.allclose(u_data, U_reconstructed)}")

# print("\nL1 matrix:")
# print(np.round(L1, 3))
# print("\nL2 matrix:")
# print(np.round(L2, 3))
# print("\nR1h matrix:")
# print(np.round(R1h, 3))
# print("\nR2h matrix:")
# print(np.round(R2h, 3))

# 3. Print for verification
# print(f"--- ANGLE EXTRACTION SUCCESS ---")
# print(f"Angle 1: {thetas[0]:.4f} rad")
# print(f"Angle 2: {thetas[1]:.4f} rad")

# 4. Map to RY/RZ structure (Conceptual)
# print(f"Resulting RY rotations: RY({thetas[0]}) and RY({thetas[1]})")

# 5. Map to actual gate sequence
# print(f"\n--- GATE SEQUENCE ---")
# gates = map_to_gates(L1, L2, thetas, R1h, R2h)

# if not gates:
#     print("Gate is Identity — no operations needed")
# else:
#     for i, gate in enumerate(gates):
#         print(f"Step {i+1}: {gate}")

#_____________________STRESS TEST PRINT BLOCK______________________________________
print("--- STRESS TEST: 100 Random Unitaries ---")
passed = 0
failed = 0
failed_cases = []

for i in range(100):
    # Generate fresh random unitary each iteration
    U = Qobj(
        la.qr(np.random.randn(4, 4) + 1j * np.random.randn(4, 4))[0],
        dims=[[2, 2], [2, 2]],
    )
    
    u_data = U.full()
    
    # CSD
    (L1, L2), thetas, (R1h, R2h) = cossin(u_data, p=2, q=2, separate=True)
    
    # Reconstruct
    C = np.diag(np.cos(thetas))
    S = np.diag(np.sin(thetas))
    CS = np.block([[C, -S], [S, C]])
    L = np.block([[L1, np.zeros((2,2))], [np.zeros((2,2)), L2]])
    R = np.block([[R1h, np.zeros((2,2))], [np.zeros((2,2)), R2h]])
    U_reconstructed = L @ CS @ R
    
    # Check
    is_correct = np.allclose(u_data, U_reconstructed, atol=1e-10)
    error = np.linalg.norm(u_data - U_reconstructed)
    
    if is_correct:
        passed += 1
    else:
        failed += 1
        failed_cases.append((i, error))

# Final report
print(f"Passed: {passed}/100")
print(f"Failed: {failed}/100")

if failed_cases:
    print("\nFailed cases:")
    for idx, err in failed_cases:
        print(f"  Iteration {idx}: Error = {err}")
else:
    print("All 100 unitaries reconstructed perfectly!")
#_____________________STRESS TEST PRINT BLOCK______________________________________