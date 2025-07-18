#!/usr/bin/env bash
# this_file: scripts/test.sh
# Test script for geminpy package

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="geminpy"
MIN_COVERAGE=80

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if uv is available
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "uv is not installed. Please install uv first:"
        print_info "curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
}

# Run linting
run_lint() {
    print_info "Running linting..."
    
    # Create test environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        uv venv .venv
        source .venv/bin/activate
        uv pip install -e ".[dev,test]" || {
            print_warning "Failed to install with macdefaultbrowsy dependency, trying without..."
            uv pip install pytest pytest-cov pytest-xdist pytest-asyncio mypy ruff fire playwright requests platformdirs loguru rich aiohttp
        }
    else
        source .venv/bin/activate
    fi
    
    # Run ruff check
    print_info "Running ruff check..."
    ruff check src/$PROJECT_NAME tests/ || {
        print_error "Ruff check failed"
        return 1
    }
    
    # Run ruff format check
    print_info "Running ruff format check..."
    ruff format --check src/$PROJECT_NAME tests/ || {
        print_error "Ruff format check failed"
        return 1
    }
    
    print_success "Linting passed"
}

# Run type checking
run_type_check() {
    print_info "Running type checking..."
    
    source .venv/bin/activate
    mypy src/$PROJECT_NAME tests/ || {
        print_error "Type checking failed"
        return 1
    }
    
    print_success "Type checking passed"
}

# Run tests
run_tests() {
    print_info "Running tests..."
    
    source .venv/bin/activate
    
    # Run tests with coverage
    PYTHONPATH=src python -m pytest \
        --cov=src/$PROJECT_NAME \
        --cov-report=term-missing \
        --cov-report=xml \
        --cov-report=html \
        --cov-fail-under=$MIN_COVERAGE \
        -v \
        tests/ || {
        print_error "Tests failed"
        return 1
    }
    
    print_success "Tests passed with coverage >= $MIN_COVERAGE%"
}

# Run security checks
run_security_check() {
    print_info "Running security checks..."
    
    source .venv/bin/activate
    
    # Check for known vulnerabilities (if safety is available)
    if command -v safety &> /dev/null; then
        safety check || {
            print_warning "Security check found vulnerabilities"
        }
    else
        print_info "Safety not available, skipping security check"
    fi
    
    # Use ruff's security rules (already included in our ruff config)
    print_success "Security checks completed"
}

# Run benchmarks
run_benchmarks() {
    print_info "Running benchmarks..."
    
    source .venv/bin/activate
    
    # Run benchmark tests if they exist
    if [ -f "tests/test_benchmark.py" ]; then
        python -m pytest tests/test_benchmark.py --benchmark-only || {
            print_warning "Benchmarks failed"
        }
    else
        print_info "No benchmark tests found"
    fi
    
    print_success "Benchmarks completed"
}

# Generate test report
generate_report() {
    print_info "Generating test report..."
    
    # Coverage report is already generated in run_tests
    if [ -f "htmlcov/index.html" ]; then
        print_success "Coverage report generated: htmlcov/index.html"
    fi
    
    if [ -f "coverage.xml" ]; then
        print_success "Coverage XML report generated: coverage.xml"
    fi
}

# Main function
main() {
    print_info "Starting test suite for $PROJECT_NAME..."
    
    check_uv
    
    # Parse command line arguments
    RUN_LINT=true
    RUN_TYPE_CHECK=true
    RUN_TESTS=true
    RUN_SECURITY=false
    RUN_BENCHMARKS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-lint)
                RUN_LINT=false
                shift
                ;;
            --no-type-check)
                RUN_TYPE_CHECK=false
                shift
                ;;
            --no-tests)
                RUN_TESTS=false
                shift
                ;;
            --security)
                RUN_SECURITY=true
                shift
                ;;
            --benchmarks)
                RUN_BENCHMARKS=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --no-lint       Skip linting"
                echo "  --no-type-check Skip type checking"
                echo "  --no-tests      Skip tests"
                echo "  --security      Run security checks"
                echo "  --benchmarks    Run benchmarks"
                echo "  --help          Show this help"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Run checks
    if [ "$RUN_LINT" = true ]; then
        run_lint || exit 1
    fi
    
    if [ "$RUN_TYPE_CHECK" = true ]; then
        run_type_check || exit 1
    fi
    
    if [ "$RUN_TESTS" = true ]; then
        run_tests || exit 1
    fi
    
    if [ "$RUN_SECURITY" = true ]; then
        run_security_check
    fi
    
    if [ "$RUN_BENCHMARKS" = true ]; then
        run_benchmarks
    fi
    
    generate_report
    
    print_success "All tests completed successfully!"
}

# Run main function
main "$@"