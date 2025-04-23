# src/profundc/services/kill.py

import os
import signal

from profundc.core.monitor import get_hearthstone_pid, report_error

def kill_game(on_error=None):
    """
    Send SIGTERM to Hearthstone if running.
    Returns True on success, False otherwise.
    """
    pid = get_hearthstone_pid()
    if not pid:
        return (on_error or report_error)("Hearthstone not running.") or False

    try:
        os.kill(pid, signal.SIGTERM)
        return True
    except Exception as e:
        return (on_error or report_error)(f"Failed to kill (PID {pid}): {e}") or False
