from profundc.core.paths import *
from profundc.core.logs import *
from profundc.core.monitor import *

def get_all_logged_game_ips():
    """
    Locate the Hearthstone Logs directory, pick the newest subdirectory,
    find the log file, and return a set of all discovered server IPs.
    """
    log_dir = get_hearthstone_log_dir()
    if not log_dir:
        return set()

    latest = get_latest_dir()
    if not latest:
        return set()

    net_log_file = find_game_net_logger()
    if not net_log_file:
        return set()

    return get_ips_from_hslog(net_log_file)


def get_active_game_ip():
    """
    Check if any of the server IPs from logs has an active
    connection by Hearthstone. Returns the active IP string, or None.
    """
    # Find the Hearthstone process
    pid = get_hearthstone_pid()
    if not pid:
        return None

    # Get all logged server IPs
    ips = get_all_logged_game_ips()
    if not ips:
        return None

    # Check for an active connection matching any IP
    return get_active_ip(ips, pid)