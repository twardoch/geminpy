#!/usr/bin/env bash
# this_file: scripts/build.sh
# Build script for geminpy package

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="geminpy"
DIST_DIR="dist"
BUILD_DIR="build"

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

# Clean previous builds
clean_build() {
    print_info "Cleaning previous builds..."
    rm -rf "$DIST_DIR" "$BUILD_DIR" *.egg-info
    uvx hatch clean
    print_success "Build directories cleaned"
}

# Build wheel and sdist
build_package() {
    print_info "Building package..."
    uvx hatch build
    print_success "Package built successfully"
}

# Create binary executable
build_binary() {
    print_info "Building binary executable..."
    
    # Create temporary environment for binary building
    if [ -d ".build_env" ]; then
        rm -rf .build_env
    fi
    
    uv venv .build_env
    source .build_env/bin/activate
    
    # Install dependencies for binary building
    uv pip install pyinstaller
    uv pip install -e .
    
    # Build binary
    pyinstaller --onefile \
        --name "$PROJECT_NAME" \
        --add-data "src/$PROJECT_NAME:$PROJECT_NAME" \
        --collect-all loguru \
        --collect-all rich \
        --collect-all fire \
        --collect-all playwright \
        --hidden-import=playwright \
        --hidden-import=playwright.sync_api \
        --hidden-import=playwright.async_api \
        "src/$PROJECT_NAME/__main__.py"
    
    deactivate
    rm -rf .build_env
    
    print_success "Binary built successfully: dist/$PROJECT_NAME"
}

# Main function
main() {
    print_info "Starting build process for $PROJECT_NAME..."
    
    check_uv
    clean_build
    build_package
    
    # Build binary if requested
    if [[ "${1:-}" == "--binary" ]]; then
        build_binary
    fi
    
    print_success "Build completed successfully!"
    print_info "Artifacts available in: $DIST_DIR/"
    ls -la "$DIST_DIR/"
}

# Run main function
main "$@"