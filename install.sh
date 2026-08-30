#!/usr/bin/env bash
#
# Forge installer - creates a virtual environment and installs everything.
#
# Usage:
#   ./install.sh          install into .venv (project-local)
#   ./install.sh --global additionally symlink `forge` into ~/.local/bin
#
set -euo pipefail

cd "$(dirname "$0")"

BOLD="\033[1m"
GREEN="\033[32m"
RED="\033[31m"
RESET="\033[0m"
GLOBAL=false
if [[ "${1:-}" == "--global" ]]; then
    GLOBAL=true
fi

info()  { echo -e "${BOLD}$*${RESET}"; }
step()  { echo -e "  ${GREEN}->${RESET} $*"; }
fail()  { echo -e "${RED}Error: $*${RESET}" >&2; exit 1; }

# --- check python ---------------------------------------------------------
PYTHON="python3"
command -v "$PYTHON" >/dev/null 2>&1 || fail "$PYTHON not found - install Python >= 3.10 first"

# --- venv ----------------------------------------------------------------
info "Forge installer"

if [ ! -d .venv ]; then
    step "Creating virtual environment (.venv)..."
    "$PYTHON" -m venv .venv
else
    step "Using existing .venv"
fi

step "Activating venv and installing dependencies..."
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip --quiet
pip install -e . --quiet

step "Done! Forge is installed."

if [ "$GLOBAL" = true ]; then
    BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
    mkdir -p "$BIN_DIR"
    TARGET="$BIN_DIR/forge"
    if [ -e "$TARGET" ] && [ "$(readlink -f "$TARGET")" != "$(readlink -f .venv/bin/forge)" ]; then
        fail "'$TARGET' already exists"
    fi
    ln -sf "$(readlink -f .venv/bin/forge)" "$TARGET"
    step "Linked 'forge' into $BIN_DIR (available on PATH)"
fi

echo
info "Usage:"
echo "  source .venv/bin/activate   # then:"
echo "  forge                       # analyze current project"
echo "  forge /path/to/project      # analyze any project"
echo "  forge stats | tree | git | health"
[[ "$GLOBAL" == true ]] && echo "  (already on PATH - just run: forge)"