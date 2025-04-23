import re
import os
from profundc.core.logs import *
from pathlib import Path
from configobj import ConfigObj

def get_steam_library_paths():
    """
    Return all Steam libraryfolders.vdf roots, including
    both native and Flatpak Steam installs.
    """
    steamapps_roots = [
        # native Steam
        Path.home() / ".steam/steam/steamapps",
        Path.home() / ".local/share/Steam/steamapps",
        # Flatpak Steam (old layout)
        Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps",
        # Flatpak Steam (new layout)
        Path.home() / ".var/app/com.valvesoftware.Steam/data/Steam/steamapps",
    ]

    vdf_re = re.compile(r'^\s*"\d+"\s*"\s*(.+?)\s*"$')
    libraries = []

    for steamapps in steamapps_roots:
        vdf = steamapps / "libraryfolders.vdf"
        if not vdf.exists():
            continue

        # parse each "N" "<path>" line
        for line in vdf.read_text(errors="ignore").splitlines():
            m = vdf_re.match(line)
            if m:
                libraries.append(Path(m.group(1)) / "steamapps")

        # always include the default steamapps
        libraries.append(steamapps)
        # stop after the first valid steamapps folder
        break
    return libraries


def get_hearthstone_prefixes():
    "Return list of all HS prefixes incase different proton versions are used"
    prefixes = []
    for steamapps in get_steam_library_paths():
        compat = steamapps / "compatdata"
        if not compat.is_dir():
            continue
        for appdir in compat.iterdir():
            pfx = appdir / "pfx"
            install = (pfx / "drive_c" / "Program Files (x86)" / "Hearthstone")
            if install.is_dir():
                prefixes.append(pfx)       
    return prefixes


def get_recent_hearthstone_prefix():
    "Return the most recently modified HS prefix (or None)."
    prefixes = get_hearthstone_prefixes()
    if not prefixes:
        return None
    return max(prefixes, key=lambda p: p.stat().st_mtime)


def get_hearthstone_install():
    "Return the 'Program Files (x86)/Hearthstone' directory inside the most recently modified HS prefix. (or None)"
    prefix = get_recent_hearthstone_prefix()
    if not prefix:
        return None
    install = prefix / "drive_c" / "Program Files (x86)" / "Hearthstone"
    return install if install.exists() else None



def set_log_config(cfg_name='log.config'):
    """
    Locate (or create) the Hearthstone log.config and ensure
    the Network section has the three required keys.
    Returns the Path to log.config or None if prefix wasn't found.
    """
    prefix = get_recent_hearthstone_prefix()
    if not prefix:
        return None

    cfg_path = (
        prefix
        / "drive_c" / "users" / "steamuser"
        / "AppData" / "Local"
        / "Blizzard" / "Hearthstone"
        / cfg_name
    )

    # Ensure directory exists
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    # If file missing, bootstrap it with just [Network]
    if not cfg_path.exists():
        cfg_path.write_text("[Network]\n")

    # Load with comments preserved
    config = ConfigObj(str(cfg_path), encoding='utf8', list_values=False)

    # Ensure the section exists
    net = config.setdefault('Network', {})

    # The three keys we care about
    desired = {
        'LogLevel':     '1',
        'FilePrinting': 'true',
        'Verbose':      'true',
    }

    # Update only those keys
    changed = False
    for k, v in desired.items():
        if net.get(k) != v:
            net[k] = v
            changed = True

    # Write back (in‑place, comments intact) if needed
    if changed:
        config.write()
    return cfg_path



def get_hearthstone_log_dir():
    """
    Return the Logs directory under the Hearthstone prefix,
    or None if not found.
    """
    hs_install = get_hearthstone_install()
    if not hs_install:
        return None
    logs = hs_install / "Logs"
    return logs if logs.is_dir() else None


def get_latest_dir():
    if get_hearthstone_log_dir():
        base = Path(get_hearthstone_log_dir())
        subdirs = [d for d in base.iterdir() if d.is_dir()]
        if not subdirs:
            return None
        latest_dir = max(subdirs, key=lambda d: d.stat().st_mtime)
        return latest_dir
    else:
        return None

def find_game_net_logger(log_filename='GameNetLogger.log'):
    if get_latest_dir():
        log_path = get_latest_dir() / log_filename
        if log_path.exists():
            # print(f"Found log at: {log_path}")
            return log_path
    else:
        return None


