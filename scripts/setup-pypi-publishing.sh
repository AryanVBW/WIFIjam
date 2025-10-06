#!/bin/bash
# Setup script for PyPI publishing with OIDC
# This script helps configure PyPI trusted publishing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_OWNER="AryanVBW"
REPO_NAME="WIFIjam"
PACKAGE_NAME="wifijam"
WORKFLOW_NAME="publish.yml"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  WIFIjam PyPI Publishing Setup with OIDC                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print step
print_step() {
    echo -e "${GREEN}▶ $1${NC}"
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Check if running in correct directory
if [ ! -f "setup.py" ] || [ ! -d "wifijam" ]; then
    print_error "This script must be run from the WIFIjam repository root!"
    exit 1
fi

print_success "Running in correct directory"
echo ""

# Step 1: Check current version
print_step "Step 1: Checking current version"
CURRENT_VERSION=$(grep -oP '__version__\s*=\s*"\K[^"]+' wifijam/__init__.py)
print_info "Current version: $CURRENT_VERSION"
echo ""

# Step 2: Verify workflow files
print_step "Step 2: Verifying workflow files"
if [ -f ".github/workflows/publish.yml" ]; then
    print_success "Publish workflow exists"
else
    print_error "Publish workflow not found!"
    exit 1
fi

if [ -f ".github/workflows/version-bump.yml" ]; then
    print_success "Version bump workflow exists"
else
    print_warning "Version bump workflow not found (optional)"
fi
echo ""

# Step 3: Check Git configuration
print_step "Step 3: Checking Git configuration"
GIT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$GIT_REMOTE" == *"$REPO_OWNER/$REPO_NAME"* ]]; then
    print_success "Git remote configured correctly"
else
    print_warning "Git remote: $GIT_REMOTE"
    print_warning "Expected: github.com/$REPO_OWNER/$REPO_NAME"
fi
echo ""

# Step 4: Display PyPI configuration
print_step "Step 4: PyPI Trusted Publisher Configuration"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Configure these EXACT values on PyPI:${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  PyPI Project Name:  $PACKAGE_NAME"
echo "  Owner:              $REPO_OWNER"
echo "  Repository name:    $REPO_NAME"
echo "  Workflow name:      $WORKFLOW_NAME"
echo "  Environment name:   pypi"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Step 5: Display Test PyPI configuration
print_step "Step 5: Test PyPI Trusted Publisher Configuration"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Configure these EXACT values on Test PyPI:${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  PyPI Project Name:  $PACKAGE_NAME"
echo "  Owner:              $REPO_OWNER"
echo "  Repository name:    $REPO_NAME"
echo "  Workflow name:      $WORKFLOW_NAME"
echo "  Environment name:   testpypi"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Step 6: Instructions
print_step "Step 6: Setup Instructions"
echo ""
echo "1. Configure PyPI Trusted Publisher:"
echo "   → Go to: https://pypi.org/manage/account/publishing/"
echo "   → Click 'Add a new pending publisher'"
echo "   → Enter the values shown above"
echo ""
echo "2. Configure Test PyPI Trusted Publisher:"
echo "   → Go to: https://test.pypi.org/manage/account/publishing/"
echo "   → Click 'Add a new pending publisher'"
echo "   → Enter the values shown above"
echo ""
echo "3. Create GitHub Environments:"
echo "   → Go to: https://github.com/$REPO_OWNER/$REPO_NAME/settings/environments"
echo "   → Create environment: 'pypi' (lowercase)"
echo "   → Create environment: 'testpypi' (lowercase)"
echo ""
echo "4. Test the setup:"
echo "   → Create a test tag: git tag -a v$CURRENT_VERSION-rc.1 -m 'Test release'"
echo "   → Push the tag: git push origin v$CURRENT_VERSION-rc.1"
echo "   → Check Actions: https://github.com/$REPO_OWNER/$REPO_NAME/actions"
echo ""

# Step 7: Verification checklist
print_step "Step 7: Verification Checklist"
echo ""
echo "Before creating a production release, verify:"
echo ""
echo "  [ ] PyPI trusted publisher configured"
echo "  [ ] Test PyPI trusted publisher configured"
echo "  [ ] GitHub environment 'pypi' created"
echo "  [ ] GitHub environment 'testpypi' created"
echo "  [ ] Workflow has 'id-token: write' permission"
echo "  [ ] All tests passing locally"
echo "  [ ] Version number is unique"
echo ""

# Step 8: Quick commands
print_step "Step 8: Quick Commands"
echo ""
echo "Test with pre-release:"
echo "  git tag -a v$CURRENT_VERSION-rc.1 -m 'Release candidate 1'"
echo "  git push origin v$CURRENT_VERSION-rc.1"
echo ""
echo "Create production release:"
echo "  git tag -a v$CURRENT_VERSION -m 'WIFIjam v$CURRENT_VERSION'"
echo "  git push origin v$CURRENT_VERSION"
echo ""
echo "Check workflow status:"
echo "  https://github.com/$REPO_OWNER/$REPO_NAME/actions"
echo ""

# Step 9: Documentation
print_step "Step 9: Documentation"
echo ""
echo "For detailed instructions, see:"
echo "  → PYPI_TRUSTED_PUBLISHER_FIX.md"
echo "  → AUTOMATIC_VERSIONING_GUIDE.md"
echo "  → PYPI_SETUP_GUIDE.md"
echo ""

# Final message
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Setup information displayed successfully!                 ║${NC}"
echo -e "${GREEN}║  Follow the instructions above to complete setup.          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Ask if user wants to open URLs
read -p "Open PyPI configuration pages in browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Opening URLs..."
    
    # Try to open URLs (works on macOS and Linux)
    if command -v open &> /dev/null; then
        # macOS
        open "https://pypi.org/manage/account/publishing/"
        open "https://test.pypi.org/manage/account/publishing/"
        open "https://github.com/$REPO_OWNER/$REPO_NAME/settings/environments"
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open "https://pypi.org/manage/account/publishing/"
        xdg-open "https://test.pypi.org/manage/account/publishing/"
        xdg-open "https://github.com/$REPO_OWNER/$REPO_NAME/settings/environments"
    else
        print_warning "Could not open URLs automatically. Please open them manually."
    fi
fi

echo ""
print_success "Setup script completed!"

