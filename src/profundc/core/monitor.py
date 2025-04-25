# src/profundc/core/monitor.py
import psutil
import pathlib
import re

def report_error(msg):
    # "Default error hook—CLI or GUI can override this."
    print(f"[ERROR] {msg}")

def get_hearthstone_pids():
    # "Return the PID of the Hearthstone process if running, else None."
    hs_pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info.get('name') or ""
            if "hearthstone.exe" in name.lower():
                hs_pids.append(proc.info['pid'])
        except psutil.Error:
            continue
    if not hs_pids:
        return None
    return hs_pids

def get_active_interface(settings=None):
    """
    Auto‑detects the best IPv4 network interface, or honors a user override
    in settings.data['interface'] if present & valid.
    """
    # User override
    if settings:
        override = settings.data.get("interface") or ""
        if override:
            if override in psutil.net_if_addrs():
                return override
            report_error(f"Interface '{override}' not found, falling back to auto‑detect.")

    # Auto‑detect
    addrs    = psutil.net_if_addrs()
    stats    = psutil.net_if_stats()
    counters = psutil.net_io_counters(pernic=True)

    best, best_score, best_traffic = None, -1, 0
    for iface, iface_addrs in addrs.items():
        if iface.startswith(("lo", "virbr", "veth", "docker", "br-")):
            continue
        s = stats.get(iface)
        if not (s and s.isup):
            continue
        has_ipv4 = any(a.family.name == 'AF_INET' for a in iface_addrs)
        traffic = counters.get(iface).bytes_recv if iface in counters else 0

        score = (2 if s.isup else 0) + (2 if has_ipv4 else 0) + (1 if traffic>0 else 0)
        if score > best_score or (score == best_score and traffic > best_traffic):
            best, best_score, best_traffic = iface, score, traffic

    return best

def get_active_ip(ips, pid):
    # print("Checking if any IP in log file is currently active...")
    try:
        if pid is not None:
            conns = psutil.Process(pid).connections(kind="inet")
        else:
            conns = psutil.net_connections(kind="inet")
    except psutil.NoSuchProcess:
        # print(f"PID {pid} not found")
        return False

    for conn in conns:
        if conn.raddr and conn.raddr.ip in ips:
            # print(f"Connection at {conn.raddr.ip} looks active.")
            return conn.raddr.ip

    # print("Looks like there are no game connections active")
    return False
