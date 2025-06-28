#!/usr/bin/env python3
"""
Test runner for PyWeb project
Run all tests with: python tests/run_all_tests.py
"""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """Discover and run all tests"""
    print("🔬 Running PyWeb Test Suite...")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        print("\nNote: Some failures may be expected due to known bugs in the codebase.")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1) 