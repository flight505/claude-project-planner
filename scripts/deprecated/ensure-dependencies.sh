#!/usr/bin/env bash
#
# ensure-dependencies.sh
# Background dependency installer for claude-project-planner
#
# This script installs all required dependencies for /full-plan workflow.
# It attempts pip first (user preference), then falls back to uv if pip fails.
#
# Usage:
#   ./scripts/ensure-dependencies.sh [--mode full|minimal|gemini]
#
# Output:
#   - Logs to /tmp/claude-planner-deps.log
#   - Status to /tmp/claude-planner-deps-status.json
#

set -euo pipefail

# Configuration
LOG_FILE="${TMPDIR:-/tmp}/claude-planner-deps.log"
STATUS_FILE="${TMPDIR:-/tmp}/claude-planner-deps-status.json"
REQUIREMENTS_FILE="$(dirname "$0")/../requirements-full-plan.txt"
MAX_TIMEOUT_SECONDS=600  # 10 minutes max

# Parse arguments
MODE="${1:-full}"

# Initialize logging
exec > >(tee -a "$LOG_FILE") 2>&1
echo "[$(date)] ===== Dependency Installation Started (mode: $MODE) ====="

# Initialize status file
write_status() {
    local status="$1"
    local progress="$2"
    local current="${3:-}"

    cat > "$STATUS_FILE" << EOF
{
  "status": "$status",
  "progress": $progress,
  "current": "$current",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "log_file": "$LOG_FILE"
}
EOF
}

write_status "starting" 0 ""

# Get list of required packages based on mode
get_required_packages() {
    local mode="$1"

    # Parse requirements file, excluding comments and optional packages
    local packages=()

    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue

        # Skip Google Gemini packages unless mode is gemini
        if [[ "$line" =~ google-genai ]] && [[ "$mode" != "gemini" ]]; then
            continue
        fi

        # Skip optional packages unless mode is full
        if [[ "$line" =~ aiofiles|httpx ]] && [[ "$mode" == "minimal" ]]; then
            continue
        fi

        # Extract package name (before >= or ==)
        package=$(echo "$line" | sed 's/[><=].*//' | xargs)
        [[ -n "$package" ]] && packages+=("$package")
    done < "$REQUIREMENTS_FILE"

    echo "${packages[@]}"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Try installing a package with pip
install_with_pip() {
    local package="$1"
    echo "[$(date)] Attempting to install $package with pip..."

    if python3 -m pip install "$package" --quiet --no-warn-script-location; then
        echo "[$(date)] ✓ Successfully installed $package with pip"
        return 0
    else
        echo "[$(date)] ✗ Failed to install $package with pip"
        return 1
    fi
}

# Try installing a package with uv
install_with_uv() {
    local package="$1"
    echo "[$(date)] Attempting to install $package with uv..."

    if uv pip install "$package" --quiet; then
        echo "[$(date)] ✓ Successfully installed $package with uv"
        return 0
    else
        echo "[$(date)] ✗ Failed to install $package with uv"
        return 1
    fi
}

# Install a single package with fallback
install_package() {
    local package="$1"

    # Try pip first (user preference from CLAUDE.md)
    if install_with_pip "$package"; then
        return 0
    fi

    # Fallback to uv
    echo "[$(date)] pip failed, trying uv as fallback..."
    if command_exists uv; then
        if install_with_uv "$package"; then
            return 0
        fi
    else
        echo "[$(date)] ⚠ uv not found, cannot use fallback"
    fi

    echo "[$(date)] ✗ Failed to install $package with both pip and uv"
    return 1
}

# Check if a package is already installed
is_installed() {
    local package="$1"

    # Map package name to module name for imports
    local module_name="$package"
    case "$package" in
        "python-dotenv")
            module_name="dotenv"
            ;;
        "pyyaml")
            module_name="yaml"
            ;;
        "python-pptx")
            module_name="pptx"
            ;;
        "pillow")
            module_name="PIL"
            ;;
        "google-genai")
            module_name="google.genai"
            ;;
    esac

    python3 -c "import $module_name" 2>/dev/null
}

# Main installation loop
main() {
    local start_time=$(date +%s)

    # Get packages to install
    local packages=($(get_required_packages "$MODE"))
    local total=${#packages[@]}

    if [[ $total -eq 0 ]]; then
        echo "[$(date)] No packages to install for mode: $MODE"
        write_status "complete" 100 ""
        return 0
    fi

    echo "[$(date)] Found $total packages to check/install"

    local current=0
    local failed_packages=()

    for package in "${packages[@]}"; do
        ((current++))
        local progress=$((current * 100 / total))

        write_status "installing" "$progress" "$package"
        echo ""
        echo "[$(date)] [$current/$total] Processing $package..."

        # Check if already installed
        if is_installed "$package"; then
            echo "[$(date)] ✓ $package already installed, skipping"
            continue
        fi

        # Install package with fallback
        if ! install_package "$package"; then
            failed_packages+=("$package")
        fi

        # Check timeout
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        if [[ $elapsed -gt $MAX_TIMEOUT_SECONDS ]]; then
            echo "[$(date)] ⚠ Timeout reached ($MAX_TIMEOUT_SECONDS seconds), stopping"
            write_status "timeout" "$progress" "$package"
            return 1
        fi
    done

    # Final status
    if [[ ${#failed_packages[@]} -eq 0 ]]; then
        write_status "complete" 100 ""
        echo ""
        echo "[$(date)] ===== All dependencies installed successfully ====="
        return 0
    else
        write_status "partial" "$progress" "$(IFS=,; echo "${failed_packages[*]}")"
        echo ""
        echo "[$(date)] ===== Installation completed with errors ====="
        echo "[$(date)] Failed packages: ${failed_packages[*]}"
        return 1
    fi
}

# Run main function
if main; then
    exit 0
else
    exit 1
fi
