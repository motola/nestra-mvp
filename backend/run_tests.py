#!/usr/bin/env python
"""Test runner with correct PYTHONPATH setup."""

import sys
import unittest

# Add src to path so imports work
sys.path.insert(0, "src")

if __name__ == "__main__":
    # Explicitly run known test modules
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # Load test modules explicitly to avoid discovery issues
    from integrations.august.tests import test_august
    from integrations.bluetooth.tests import test_bluetooth
    from tests.identity import test_domain, test_repository_models, test_signup_service

    suite.addTests(loader.loadTestsFromModule(test_signup_service))
    suite.addTests(loader.loadTestsFromModule(test_domain))
    suite.addTests(loader.loadTestsFromModule(test_repository_models))
    suite.addTests(loader.loadTestsFromModule(test_bluetooth))
    suite.addTests(loader.loadTestsFromModule(test_august))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
