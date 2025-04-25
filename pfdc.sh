#!/usr/bin/env bash
# pfdc.sh — bootstrap & enter ProfunDC virtualenv (best-practice auto-activate)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
VENV_DIR="$ROOT/.venv-pfdc"
INIT_FLAG="$VENV_DIR/.initialized"
PYTHON=${PYTHON:-python3}

have() { command -v "$1" &>/dev/null; }
info() { printf '→ %s\n' "$*"; }
err()  { printf '✖ %s\n' "$*" >&2; }

create_venv_and_install() {
    info "Creating virtual environment at $VENV_DIR"
    if ! "$PYTHON" -m venv "$VENV_DIR"; then
        info "‘$PYTHON -m venv’ failed—falling back to virtualenv"
        virtualenv "$VENV_DIR"
    fi

    info "Installing Python dependencies"
    # disable default prompt mangling
    export VIRTUAL_ENV_DISABLE_PROMPT=0
    export VIRTUAL_ENV_PROMPT="(pfdc) "
    # activate, install, then deactivate
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel
    if [[ -f "$ROOT/setup.py" || -f "$ROOT/pyproject.toml" ]]; then
        pip install -e "$ROOT"
    else
        pip install profundc
    fi
    deactivate

    touch "$INIT_FLAG"
    info "Virtual environment setup complete."
}

launch_shell() {
    # Determine user’s shell
    shell_name=$(basename "${SHELL:-bash}")
    case "$shell_name" in
        bash|zsh|ksh)
            exec "$shell_name" -i -c "export VIRTUAL_ENV_DISABLE_PROMPT=0; export VIRTUAL_ENV_PROMPT='(pfdc) '; source '$VENV_DIR/bin/activate'; exec $shell_name"
            ;;
        fish)
            exec fish -i -C "source '$VENV_DIR/bin/activate.fish'; exec fish"
            ;;
        *)
            info "Unsupported shell '$shell_name'—falling back to sh"
            exec sh -i -c "source '$VENV_DIR/bin/activate'; exec sh"
            ;;
    esac
}

main() {
    # 1) Check system dependencies
    local missing=0
    for cmd in tcpkill nsenter python3; do
        if ! have "$cmd"; then
            err "Missing system dependency: $cmd"
            err "Please install it via your distro’s package manager before continuing."
            missing=1
        fi
    done
    [[ $missing -eq 1 ]] && exit 1

    # 2) Bootstrap venv if needed
    if [[ ! -f "$INIT_FLAG" ]]; then
        info "First-time setup…"
        create_venv_and_install
    else
        info "Virtual environment already exists."
    fi

    # 3) Show quick help and enter venv shell
    echo
    info "Launching ProfunDC shell (type 'exit' to return)..."
    "$VENV_DIR/bin/pfdc" -h | head -n 10
    echo
    launch_shell
}

main "$@"
