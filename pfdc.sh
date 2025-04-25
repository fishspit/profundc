#!/usr/bin/env bash
# pfdc.sh — one-time venv setup and launch wrapper for ProfunDC
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
VENV_DIR="$ROOT/.venv-pfdc"
INIT_FLAG="$VENV_DIR/.initialized"
PYTHON=${PYTHON:-python3}

# Helpers
have() { command -v "$1" &>/dev/null; }
info() { printf '→ %s\n' "$*"; }
err()  { printf '✖ %s\n' "$*" >&2; }

create_venv_and_install() {
    info "Creating virtual environment at $VENV_DIR"
    if ! "$PYTHON" -m venv "$VENV_DIR"; then
        info "‘$PYTHON -m venv’ failed—falling back to virtualenv"
        virtualenv "$VENV_DIR"
    fi

    info "Activating virtual environment"
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"

    info "Upgrading pip, setuptools, wheel"
    pip install --upgrade pip setuptools wheel

    info "Installing ProfunDC package"
    if [[ -f "$ROOT/setup.py" || -f "$ROOT/pyproject.toml" ]]; then
        pip install -e "$ROOT"
    else
        pip install profundc
    fi

    info "Writing pfdc shim"
    cat > "$VENV_DIR/bin/pfdc" <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/python" -m profundc.interfaces.cli "\$@"
EOF
    chmod +x "$VENV_DIR/bin/pfdc"

    info "Writing custom bashrc for ProfunDC prompt"
    cat > "$VENV_DIR/.pfdc.bashrc" <<EOF
# ProfunDC custom interactive shell
[ -f "\$HOME/.bashrc" ] && source "\$HOME/.bashrc"
# Activate venv silently
source "$VENV_DIR/bin/activate" > /dev/null 2>&1
# Custom prompt: show venv name and current directory
export PS1="(pfdc) \w \$ "
EOF

    touch "$INIT_FLAG"
    info "Virtual environment bootstrap complete."
}

main() {
    # 1) Check system dependencies
    MISSING=0
    for cmd in tcpkill nsenter python3; do
        if ! have "$cmd"; then
            err "Missing system dependency: $cmd"
            err "Please install the required packages as listed in the README before continuing."
            MISSING=1
        fi
    done
    [[ $MISSING -eq 1 ]] && exit 1

    # 2) First-time setup or activation
    if [[ ! -f "$INIT_FLAG" ]]; then
        info "Performing first-time setup..."
        create_venv_and_install
    else
        info "Activating existing virtual environment..."
        # shellcheck disable=SC1090
        source "$VENV_DIR/bin/activate"
    fi

    # 3) Launch custom interactive shell
    echo
    info "Launching pfdc (type 'exit' to leave)..."
    pfdc -h | head -n 12
    echo
    echo "🟢 pfdc environment ready — type commands or 'exit' to leave"
    exec bash --rcfile "$VENV_DIR/.pfdc.bashrc" -i
}

main "$@"
