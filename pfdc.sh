#!/usr/bin/env bash
# pfdc.sh — one-time verbose install; then silent launches
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
VENV_DIR="$ROOT/.venv-pfdc"
INIT_FLAG="$VENV_DIR/.initialized"
PYTHON=${PYTHON:-python3}
SYS_PKGS=(dsniff util-linux iproute2)

have() { command -v "$1" &>/dev/null; }
info()  { printf '→ %s\n' "$*";       }
err()   { printf '✖ %s\n' "$*" >&2;    }

detect_pm() {
  for pm in pacman apt-get dnf zypper apk; do
    have "$pm" && { echo "$pm"; return; }
  done
  echo ""
}

install_sys_pkgs() {
  local pm="$1"
  info "Installing system dependencies: ${SYS_PKGS[*]} via $pm"
  case "$pm" in
    pacman)  sudo pacman -Sy --noconfirm "${SYS_PKGS[@]}" ;;
    apt-get) sudo apt-get update -qq && sudo apt-get install -y "${SYS_PKGS[@]}" ;;
    dnf)     sudo dnf install -y "${SYS_PKGS[@]}" ;;
    zypper)  sudo zypper -qn install "${SYS_PKGS[@]}" ;;
    apk)     sudo apk add --no-cache "${SYS_PKGS[@]}" ;;
    *) err "Unknown package manager; please install: ${SYS_PKGS[*]}"; exit 1 ;;
  esac
}

create_venv_and_install() {
  info "Creating virtual environment in $VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR"
  info "Activating virtual environment"
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
  info "Upgrading pip and wheel"
  pip install --upgrade pip wheel
  info "Installing profundc package"
  if [[ -f "$ROOT/setup.py" || -f "$ROOT/pyproject.toml" ]]; then
    pip install -e "$ROOT"
  else
    pip install profundc
  fi
  info "Virtual environment setup complete."
}

main() {
  # Determine if first-run
  if [[ ! -f "$INIT_FLAG" ]]; then
    info "First-time setup detected."
    # 1) Ensure Python exists
    info "Checking for Python interpreter: $PYTHON"
    if ! have "$PYTHON"; then
      err "python3 not found"; exit 1
    fi

    # 2) System dependencies
    info "Checking for system dependencies: ${SYS_PKGS[*]}"
    for cmd in tcpkill nsenter; do
      if ! have "$cmd"; then
        PM=$(detect_pm)
        [[ -n "$PM" ]] || { err "No supported package manager found."; exit 1; }
        install_sys_pkgs "$PM"
        break
      fi
    done
    info "System dependencies OK."

    # 3) Python venv & package
    create_venv_and_install

    # 4) Mark initialization
    touch "$INIT_FLAG"
    info "Initial setup complete."
  else
    # Subsequent runs: just activate silently
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"
  fi

  # 5) Show help banner & drop to shell
  echo
  pfdc -h | head -n 12
  echo
  echo "🟢 pfdc environment ready — type commands, or 'exit' to leave"
  exec "${SHELL:-/bin/bash}" -i
}

main "$@"
