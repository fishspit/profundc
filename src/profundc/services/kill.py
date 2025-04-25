# src/profundc/services/kill.py

import os
import signal

from profundc.core.monitor import get_hearthstone_pids, report_error

def kill_game(on_error=None):
    """
    Send SIGTERM to Hearthstone if running.
    Returns True on success, False otherwise.
    """
    pids = get_hearthstone_pids()
    if not pids:
        return (on_error or report_error)("Hearthstone not running.") or False

    try:
        for pid in pids:
            os.kill(pid, signal.SIGTERM)
        return True
    except Exception as e:
        return (on_error or report_error)(f"Failed to kill (PID {pids}): {e}") or False
