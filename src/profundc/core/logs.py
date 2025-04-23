import re
from pathlib import Path
import psutil
from profundc.core.paths import *
import configparser


def get_ips_from_hslog(log_file_path):
    """
    Scans the entire log file and returns a list of all
    IPv4 addresses seen in Network.GotoGameServe() calls.
    """
    pattern = re.compile(
        r'Network\.GotoGameServe\(\) - address=\s*'
        r'(\d{1,3}(?:\.\d{1,3}){3})'
    )
    ips = set()
    try:
        with log_file_path.open('r') as f:
            for line in f:
                for m in pattern.finditer(line):
                    ips.add(m.group(1))

        if not ips:
            return None
        else:
            # print(f"Found IPs in log file {ips}")
            return ips
        return ips

    except FileNotFoundError:
        print("GameNetLogger.log found, maybe join game and try again?")
        return []



