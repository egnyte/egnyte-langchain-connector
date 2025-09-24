"""
Comprehensive test runner for langchain-egnyte package.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description, check=True):
    """Run a command and handle output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")

    required_packages = [
        "pytest",
        "black",
        "isort",
        "flake8",
        "mypy",
        "pytest-cov",
        "pytest-asyncio",
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -e '.[dev]'")
        return False

    print("All dependencies are installed.")
    return True


def run_linting():
    """Run code linting checks."""
    print("\n" + "=" * 60)
    print("RUNNING LINTING CHECKS")
    print("=" * 60)

    success = True

    # Black formatting check
    success &= run_command(["black", "--check", "."], "Black code formatting check")

    # isort import sorting check
    success &= run_command(["isort", "--check-only", "."], "isort import sorting check")

    # flake8 linting
    success &= run_command(["flake8", "."], "flake8 linting check")

    return success


def run_type_checking():
    """Run type checking with mypy."""
    print("\n" + "=" * 60)
    print("RUNNING TYPE CHECKING")
    print("=" * 60)

    return run_command(["mypy", "egnyte_retriever/"], "mypy type checking")


def run_unit_tests():
    """Run unit tests."""
    print("\n" + "=" * 60)
    print("RUNNING UNIT TESTS")
    print("=" * 60)

    return run_command(
        [
            "pytest",
            "tests/",
            "-k",
            "not integration",
            "--cov=egnyte_retriever",
            "--cov-report=term-missing",
            "--cov-report=html",
            "-v",
        ],
        "Unit tests with coverage",
    )


def run_integration_tests():
    """Run integration tests."""
    print("\n" + "=" * 60)
    print("RUNNING INTEGRATION TESTS")
    print("=" * 60)

    # Check if integration test credentials are available
    if not (os.getenv("EGNYTE_DOMAIN") and os.getenv("EGNYTE_TOKEN")):
        print("Skipping integration tests - EGNYTE_DOMAIN and EGNYTE_TOKEN not set")
        return True

    return run_command(
        [
            "pytest",
            "tests/integration/",
            "--cov=egnyte_retriever",
            "--cov-append",
            "-v",
        ],
        "Integration tests",
    )


def run_security_checks():
    """Run security checks."""
    print("\n" + "=" * 60)
    print("RUNNING SECURITY CHECKS")
    print("=" * 60)

    success = True

    # Check if safety is installed
    try:
        import safety  # noqa: F401

        success &= run_command(
            ["safety", "check"],
            "Safety dependency vulnerability check",
            check=False,  # Don't fail on safety issues
        )
    except ImportError:
        print("Safety not installed - skipping vulnerability check")

    # Check if bandit is installed
    try:
        import bandit  # noqa: F401

        success &= run_command(
            ["bandit", "-r", "egnyte_retriever/"],
            "Bandit security scan",
            check=False,  # Don't fail on bandit issues
        )
    except ImportError:
        print("Bandit not installed - skipping security scan")

    return success


def run_build_test():
    """Test package building."""
    print("\n" + "=" * 60)
    print("TESTING PACKAGE BUILD")
    print("=" * 60)

    success = True

    # Clean previous builds
    import shutil

    for dir_name in ["build", "dist", "*.egg-info"]:
        for path in Path(".").glob(dir_name):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    # Build package
    success &= run_command(["python", "-m", "build"], "Package build")

    # Check package
    try:
        import twine  # noqa: F401

        success &= run_command(["twine", "check", "dist/*"], "Package validation")
    except ImportError:
        print("Twine not installed - skipping package validation")

    return success


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Run tests for langchain-egnyte package"
    )
    parser.add_argument(
        "--lint-only", action="store_true", help="Run only linting checks"
    )
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Run only integration tests",
    )
    parser.add_argument(
        "--no-integration", action="store_true", help="Skip integration tests"
    )
    parser.add_argument(
        "--no-security", action="store_true", help="Skip security checks"
    )
    parser.add_argument("--no-build", action="store_true", help="Skip build test")
    parser.add_argument("--fix", action="store_true", help="Fix formatting issues")

    args = parser.parse_args()

    print("EGNYTE RETRIEVER - COMPREHENSIVE TEST RUNNER")
    print("=" * 60)

    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)

    success = True

    # Fix formatting if requested
    if args.fix:
        print("\nFixing code formatting...")
        run_command(["black", "."], "Black code formatting", check=False)
        run_command(["isort", "."], "isort import sorting", check=False)
        print("Formatting fixed. Please review changes and run tests again.")
        return

    # Run specific test types based on arguments
    if args.lint_only:
        success = run_linting()
    elif args.unit_only:
        success = run_unit_tests()
    elif args.integration_only:
        success = run_integration_tests()
    else:
        # Run full test suite
        success &= run_linting()
        success &= run_type_checking()
        success &= run_unit_tests()

        if not args.no_integration:
            success &= run_integration_tests()

        if not args.no_security:
            success &= run_security_checks()

        if not args.no_build:
            success &= run_build_test()

    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if success:
        print("✅ ALL TESTS PASSED!")
        print("\nYour package is ready for deployment!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print("\nPlease fix the issues above before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()
