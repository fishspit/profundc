# src/profundc/services/disconnect.py

import shutil
import subprocess
import time
import sys
from pathlib import Path

from profundc.core.monitor import get_hearthstone_pids, get_active_interface, report_error
from profundc.services.game import get_active_game_ip

SCRIPT = (
    Path(__file__).resolve()
    .parents[1]               # src/profundc
    / 'resources'
    / 'tcpkill_packet.sh'
)

def _disconnect_script(pid, iface, server_ip, use_sudo):
    """
    Run the helper script under sudo -n (if use_sudo) or pkexec.
    Returns True on success, False on failure.
    """
    if not SCRIPT.exists():
        report_error(f"Missing helper script: {SCRIPT}")
        return False

    if use_sudo:
        elev = ["sudo", "-n"]
    else:
        elev = ["pkexec"]

    cmd = elev + [str(SCRIPT), str(pid), iface, server_ip]

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        report_error(f"Failed to spawn disconnect script: {e}")
        return False

    code = proc.wait()
    if code != 0:
        report_error(f"Disconnect script exited with code {code}")
        return False

    time.sleep(0.5)
    return True


def start_disconnect(on_error=None):
    """
    Initiate a quick network disconnect for Hearthstone by dropping one packet.
    Returns True on success, False on any failure.
    """
    pid = get_hearthstone_pids()
    if not pid:
        (on_error or report_error)("Hearthstone is not running.")
        return False

    iface = get_active_interface()
    if not iface:
        (on_error or report_error)("No active network interface found.")
        return False

    server_ip = get_active_game_ip()
    if not server_ip:
        (on_error or report_error)("No active game server found.")
        return False

    # Prompt for sudo password if sudo exists
    use_sudo = bool(shutil.which("sudo"))
    if use_sudo:
        try:
            # -v means “validate” (prompt for password if needed)
            subprocess.run(["sudo", "-v"], check=True, stdin=sys.stdin)
        except subprocess.CalledProcessError:
            (on_error or report_error)("sudo authentication failed.")
            return False

    # Waiting for packet message
    print("Waiting for packet…")
    print("Hover over in-game assets to force packet request if not triggering")

    # Perform packet drop 
    return _disconnect_script(pid[0], iface, server_ip, use_sudo)
