#!/usr/bin/env python3
"""
Comprehensive Test Runner for BMS Platform
Runs all phase test suites and full platform e2e integration test.
"""
import subprocess
import sys
import os

TESTS = [
    "test_phase1.py",
    "test_phase2.py",
    "test_phase3.py",
    "test_phase4.py",
    "test_phase5.py",
    "test_phase6.py",
    "test_phase7.py",
    "test_phase8.py",
    "test_phase9.py",
    "test_phase10_services.py",
    "test_full_platform_e2e.py"
]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = sys.executable

    print("=" * 65)
    print("  RUNNING ALL 11 BMS TEST SUITES (PHASES 1-10 + FULL E2E)")
    print("=" * 65)

    results = {}
    for t in TESTS:
        test_path = os.path.join(script_dir, t)
        print(f"--> Executing {t} ...")
        res = subprocess.run([python_exe, test_path], capture_output=True, text=True)
        if res.returncode == 0:
            results[t] = "PASS"
            print(f"    [PASS] {t}")
        else:
            results[t] = "FAIL"
            print(f"    [FAIL] {t}")
            print("--- STDOUT ---")
            print(res.stdout)
            print("--- STDERR ---")
            print(res.stderr)

    print("\n" + "=" * 65)
    print("  FINAL TEST EXECUTION SUMMARY:")
    print("=" * 65)
    for t, status in results.items():
        print(f"  {t:32} : {status}")

    passed_count = sum(1 for s in results.values() if s == "PASS")
    total_count = len(TESTS)
    print("=" * 65)
    print(f"  SCORE: {passed_count}/{total_count} PASSED")
    print("=" * 65)

    if passed_count == total_count:
        print("  CONGRATULATIONS: 100% OF TEST SUITES PASSED CLEANLY!")
        sys.exit(0)
    else:
        print(f"  WARNING: {total_count - passed_count} SUITE(S) FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
