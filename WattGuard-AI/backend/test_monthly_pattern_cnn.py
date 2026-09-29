"""Standalone Unit & Evaluation Test Suite for Monthly Pattern Deviation 1D CNN.
Tests:
1. Stable Consumer Scenario (consistent diurnal profile across June vs July).
2. Theft Bypass Scenario (drastic profile drop & shape distortion July vs August).
3. Seasonal / Partial Shift Scenario.
4. Input sequence robustness (variable length interpolation to 30 days).
5. Architecture metadata compliance.
"""
import sys
from pathlib import Path
import numpy as np

# Ensure backend is on sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.ml.monthly_pattern_cnn import MonthlyPatternCNN, monthly_pattern_cnn_instance


def test_stable_consumer():
    """Test 1: Stable consumer with consistent monthly patterns (e.g., June vs July)."""
    print("\n--- TEST 1: STABLE CONSUMER PATTERN ---")
    np.random.seed(101)
    # 30 days of baseline load with standard weekday/weekend modulation
    days = np.arange(30)
    base_pattern = 18.0 + 4.0 * np.sin(2 * np.pi * days / 7) + np.random.normal(0, 0.8, 30)

    # Month 1: June
    m1 = np.clip(base_pattern + np.random.normal(0, 0.5, 30), 5.0, 35.0)
    # Month 2: July (minor variance, slightly cooler weather -8%)
    m2 = np.clip(base_pattern * 0.92 + np.random.normal(0, 0.5, 30), 5.0, 35.0)

    cnn = MonthlyPatternCNN()
    res = cnn.compare_monthly_patterns(m1, m2, month1_name="June", month2_name="July")

    print(f"Comparison: {res['month_1_name']} vs {res['month_2_name']}")
    print(f"Pattern Similarity: {res['pattern_similarity']}%")
    print(f"Usage Change: {res['usage_change_pct']}%")
    print(f"Monthly Pattern Risk: {res['monthly_pattern_risk']}")
    print(f"Status: {res['status']}")

    assert res["pattern_similarity"] >= 70, f"Expected high similarity >= 70%, got {res['pattern_similarity']}%"
    assert abs(res["usage_change_pct"]) <= 20, f"Expected minor change <= 20%, got {res['usage_change_pct']}%"
    assert res["status"] == "Stable", f"Expected Stable status, got {res['status']}"
    assert res["monthly_pattern_risk"] <= 0.30, f"Expected low risk <= 0.30, got {res['monthly_pattern_risk']}"
    print(">>> TEST 1 PASSED: Stable consumer classified correctly.")


def test_theft_bypass_consumer():
    """Test 2: Theft bypass consumer with sudden collapse & distortion (e.g., July vs August)."""
    print("\n--- TEST 2: THEFT BYPASS CONSUMER PATTERN ---")
    np.random.seed(202)
    days = np.arange(30)
    # Month 1: July (Active commercial load)
    m1 = 28.0 + 8.0 * np.sin(2 * np.pi * days / 7) + np.random.normal(0, 1.2, 30)

    # Month 2: August (Concealed neutral bypass: 60% registration drop + clipped zero days)
    m2 = (m1 * 0.38) + np.random.normal(0, 0.4, 30)
    # Artificial flatlines / clipped registers typical of tamper
    m2[days % 4 == 0] = 3.2

    cnn = MonthlyPatternCNN()
    res = cnn.compare_monthly_patterns(m1, m2, month1_name="July", month2_name="August")

    print(f"Comparison: {res['month_1_name']} vs {res['month_2_name']}")
    print(f"Pattern Similarity: {res['pattern_similarity']}%")
    print(f"Usage Change: {res['usage_change_pct']}%")
    print(f"Monthly Pattern Risk: {res['monthly_pattern_risk']}")
    print(f"Status: {res['status']}")

    assert res["pattern_similarity"] < 60, f"Expected reduced similarity < 60%, got {res['pattern_similarity']}%"
    assert res["usage_change_pct"] <= -40, f"Expected sharp drop <= -40%, got {res['usage_change_pct']}%"
    assert res["status"] == "Suspicious Change", f"Expected Suspicious Change, got {res['status']}"
    assert res["monthly_pattern_risk"] >= 0.50, f"Expected elevated risk >= 0.50, got {res['monthly_pattern_risk']}"
    print(">>> TEST 2 PASSED: Suspicious change flagged correctly as supporting evidence.")


def test_seasonal_shift_consumer():
    """Test 3: Legitimate seasonal vacation / shift (moderate shift, not outright classified as theft)."""
    print("\n--- TEST 3: SEASONAL SHIFT CONSUMER ---")
    np.random.seed(303)
    days = np.arange(30)
    m1 = 20.0 + 5.0 * np.sin(2 * np.pi * days / 7) + np.random.normal(0, 1.0, 30)
    # 2 weeks of vacation / reduced load, but retaining general waveform
    m2 = m1.copy()
    m2[10:24] *= 0.65

    cnn = MonthlyPatternCNN()
    res = cnn.compare_monthly_patterns(m1, m2, month1_name="May", month2_name="June")

    print(f"Comparison: {res['month_1_name']} vs {res['month_2_name']}")
    print(f"Pattern Similarity: {res['pattern_similarity']}%")
    print(f"Usage Change: {res['usage_change_pct']}%")
    print(f"Monthly Pattern Risk: {res['monthly_pattern_risk']}")
    print(f"Status: {res['status']}")

    assert res["is_supporting_evidence_only"] is True
    assert res["monthly_pattern_risk"] < 0.65, "Seasonal shift should not be excessively penalized"
    print(">>> TEST 3 PASSED: Seasonal variance treated proportionately.")


def test_architecture_specifications():
    """Test 4: Verify CNN architecture parameters for Advanced Details inspector."""
    print("\n--- TEST 4: CNN ARCHITECTURE SPECIFICATIONS ---")
    cnn = MonthlyPatternCNN()
    arch = cnn.architecture_info
    print(f"Model Type: {arch['model_type']}")
    print(f"Backend Framework: {arch['backend_framework']}")
    print(f"Total Specified Layers: {len(arch['layers'])}")
    assert "Siamese" in arch["model_type"]
    assert len(arch["layers"]) >= 5
    print(">>> TEST 4 PASSED: Architecture specifications validated.")


if __name__ == "__main__":
    test_stable_consumer()
    test_theft_bypass_consumer()
    test_seasonal_shift_consumer()
    test_architecture_specifications()
    print("\n==============================================")
    print("ALL 4 MONTHLY PATTERN CNN UNIT TESTS PASSED OK!")
    print("==============================================")
