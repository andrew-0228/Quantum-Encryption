import numpy as np
import random

# --- Configuration ---
NUM_PHOTONS = 1000          # Number of photons transmitted
# Probability Eve intercepts a photon (when present)
EAVESDROP_PROB = 0.5
SECURITY_THRESHOLD = 0.11   # Max QBER allowed (11%) before key discard


def run_qkd_protocol(eavesdropper_present=False):
    """Simulates the BB84 protocol for key generation and detection."""

    # 1. Preparation (Alice's random bits and bases)
    N = NUM_PHOTONS
    alice_bits = np.random.randint(0, 2, N)
    alice_bases = np.random.randint(0, 2, N)
    bob_bases = np.random.randint(0, 2, N)

    # 2. Transmission Simulation (Includes potential eavesdropping)
    received_bits = alice_bits.copy()

    if eavesdropper_present:
        # Eve's random bases
        eve_bases = np.random.randint(0, 2, N)
        # Eve intercepts a subset
        intercept_mask = np.random.rand(N) < EAVESDROP_PROB
        # Eve introduces an error when (Alice's base != Eve's base) AND (Eve intercepts)
        eve_error_mask = intercept_mask & (alice_bases != eve_bases)

        # Flip the bit in the received stream where Eve introduced an error
        received_bits[eve_error_mask] = 1 - received_bits[eve_error_mask]

    # 3. Bob's Measurement
    bob_bits = np.zeros(N, dtype=int)
    match_mask = (alice_bases == bob_bases)

    for i in range(N):
        if match_mask[i]:
            bob_bits[i] = received_bits[i]
        else:
            # Mismatched bases introduce a 50% random error.
            bob_bits[i] = np.random.randint(0, 2)

    # 4. Basis Sifting (Keep only bits where bases matched)
    sift_mask = (alice_bases == bob_bases)
    alice_sifted_key = alice_bits[sift_mask]
    bob_sifted_key = bob_bits[sift_mask]
    sifted_length = len(alice_sifted_key)

    if sifted_length == 0:
        return None, "Key failure due to sifting."

    # 5. Security Check (Calculate QBER on a random sample)
    CHECK_SIZE = sifted_length // 4
    check_indices = np.random.choice(sifted_length, CHECK_SIZE, replace=False)

    alice_check = alice_sifted_key[check_indices]
    bob_check = bob_sifted_key[check_indices]

    errors = np.sum(alice_check != bob_check)
    qber = errors / CHECK_SIZE if CHECK_SIZE > 0 else 0

    # Remaining key size (the secret part)
    remaining_key = alice_sifted_key[~np.isin(
        np.arange(sifted_length), check_indices)]

    # 6. Final Decision and Justification
    if qber > SECURITY_THRESHOLD:
        justification = f"🚨 Eavesdropper detected (QBER: {qber*100:.2f}%). The quantum disturbance proves intrusion, so the key is discarded and the conversation is cut."
        return None, justification
    else:
        key_str = "".join(map(str, remaining_key[:10])) + "..."
        justification = f"✅ Key is SECURE (QBER: {qber*100:.2f}%). The low error rate confirms no intrusion, and the remaining key is successfully generated ({key_str})."
        return remaining_key, justification

# --------------------------------------------------------
# --- Random Execution ---
# --------------------------------------------------------


print("## 🔒 QKD Eavesdropper Detection Simulation (Random Case)")

# Randomly select the case: True or False
eavesdropper_status = random.choice([True, False])

if eavesdropper_status:
    case_description = "*EAVESDROPPER PRESENT*"
else:
    case_description = "*NO EAVESDROPPER*"

print(f"--- Running Simulation: {case_description} ---")

# Run the simulation
secret_key, justification = run_qkd_protocol(
    eavesdropper_present=eavesdropper_status)

print("-" * 50)
print(justification)
print("-" * 50)
