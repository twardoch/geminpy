#!/usr/bin/env bash
# this_file: scripts/release.sh
# Release script for geminpy package

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="geminpy"
DEFAULT_BRANCH="main"

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

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
}

# Check if working directory is clean
check_working_directory() {
    if [ -n "$(git status --porcelain)" ]; then
        print_error "Working directory is not clean. Please commit or stash changes."
        git status --short
        exit 1
    fi
}

# Check if we're on the correct branch
check_branch() {
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" != "$DEFAULT_BRANCH" ]; then
        print_error "Not on $DEFAULT_BRANCH branch (currently on $current_branch)"
        print_info "Switch to $DEFAULT_BRANCH branch to create a release"
        exit 1
    fi
}

# Check if remote is up to date
check_remote() {
    git fetch origin
    local local_commit=$(git rev-parse HEAD)
    local remote_commit=$(git rev-parse origin/$DEFAULT_BRANCH)
    
    if [ "$local_commit" != "$remote_commit" ]; then
        print_error "Local branch is not up to date with remote"
        print_info "Please pull latest changes or push local changes"
        exit 1
    fi
}

# Parse semantic version
parse_version() {
    local version="$1"
    if [[ ! "$version" =~ ^v?([0-9]+)\.([0-9]+)\.([0-9]+)(-[a-zA-Z0-9.-]+)?$ ]]; then
        print_error "Invalid version format: $version"
        print_info "Expected format: v1.2.3 or 1.2.3 (optionally with pre-release suffix)"
        exit 1
    fi
}

# Check if tag already exists
check_tag_exists() {
    local tag="$1"
    if git tag -l | grep -q "^$tag$"; then
        print_error "Tag $tag already exists"
        exit 1
    fi
}

# Get next version suggestion
suggest_next_version() {
    local latest_tag=$(git tag -l --sort=-version:refname | head -n1)
    if [ -z "$latest_tag" ]; then
        echo "v1.0.0"
        return
    fi
    
    # Remove 'v' prefix if present
    local version="${latest_tag#v}"
    
    # Split version into parts
    local major=$(echo "$version" | cut -d. -f1)
    local minor=$(echo "$version" | cut -d. -f2)
    local patch=$(echo "$version" | cut -d. -f3 | cut -d- -f1)
    
    # Suggest patch version bump
    local next_patch=$((patch + 1))
    echo "v$major.$minor.$next_patch"
}

# Run tests before release
run_tests() {
    print_info "Running tests before release..."
    ./scripts/test.sh || {
        print_error "Tests failed. Cannot proceed with release."
        exit 1
    }
    print_success "Tests passed"
}

# Build package
build_package() {
    print_info "Building package..."
    ./scripts/build.sh || {
        print_error "Build failed. Cannot proceed with release."
        exit 1
    }
    print_success "Package built successfully"
}

# Create and push tag
create_tag() {
    local version="$1"
    local message="$2"
    
    print_info "Creating tag $version..."
    git tag -a "$version" -m "$message"
    
    print_info "Pushing tag to remote..."
    git push origin "$version"
    
    print_success "Tag $version created and pushed"
}

# Upload to PyPI (optional)
upload_to_pypi() {
    print_info "Uploading to PyPI..."
    
    # Check if twine is available
    if ! command -v twine &> /dev/null; then
        print_warning "twine not found. Installing..."
        pip install twine
    fi
    
    # Upload using twine
    twine upload dist/* || {
        print_error "Failed to upload to PyPI"
        return 1
    }
    
    print_success "Successfully uploaded to PyPI"
}

# Show usage
show_usage() {
    echo "Usage: $0 <version> [options]"
    echo ""
    echo "Arguments:"
    echo "  version         Version to release (e.g., v1.2.3 or 1.2.3)"
    echo ""
    echo "Options:"
    echo "  --no-tests      Skip running tests"
    echo "  --no-build      Skip building package"
    echo "  --upload-pypi   Upload to PyPI after tagging"
    echo "  --help          Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 v1.2.3                    # Create release v1.2.3"
    echo "  $0 1.2.3 --upload-pypi       # Create release and upload to PyPI"
    echo "  $0 v1.2.3-beta.1             # Create pre-release"
    echo ""
    echo "Suggested next version: $(suggest_next_version)"
}

# Main function
main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi
    
    local version="$1"
    shift
    
    # Parse command line arguments
    RUN_TESTS=true
    BUILD_PACKAGE=true
    UPLOAD_PYPI=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-tests)
                RUN_TESTS=false
                shift
                ;;
            --no-build)
                BUILD_PACKAGE=false
                shift
                ;;
            --upload-pypi)
                UPLOAD_PYPI=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Add 'v' prefix if not present
    if [[ ! "$version" =~ ^v ]]; then
        version="v$version"
    fi
    
    print_info "Starting release process for $PROJECT_NAME $version..."
    
    # Pre-flight checks
    check_git_repo
    check_working_directory
    check_branch
    check_remote
    parse_version "$version"
    check_tag_exists "$version"
    
    # Run tests
    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi
    
    # Build package
    if [ "$BUILD_PACKAGE" = true ]; then
        build_package
    fi
    
    # Create release message
    local release_message="Release $version

Generated with geminpy release script

🚀 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
    
    # Create and push tag
    create_tag "$version" "$release_message"
    
    # Upload to PyPI if requested
    if [ "$UPLOAD_PYPI" = true ]; then
        upload_to_pypi
    fi
    
    print_success "Release $version completed successfully!"
    print_info "GitHub Actions will now build multiplatform binaries and create a GitHub release"
    print_info "Check the Actions tab in your GitHub repository for progress"
}

# Run main function
main "$@"