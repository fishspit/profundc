#!/usr/bin/env python3
import sys
import argparse
from profundc.core.monitor import get_hearthstone_pids, get_active_interface
from profundc.services.game import get_all_logged_game_ips, get_active_game_ip
from profundc.services.disconnect import start_disconnect
from profundc.services.kill import kill_game
from profundc.core.paths import *
from profundc.core.logs import *
import webbrowser 

BANNER = r"""
                      ____                __    
    ____  _________  / __/_  ______  ____/ /____
   / __ \/ ___/ __ \/ /_/ / / / __ \/ __  / ___/
  / /_/ / /  / /_/ / __/ /_/ / / / / /_/ / /__  
 / .___/_/   \____/_/  \__,_/_/ /_/\__,_/\___/  
/_/          
"""

pids = get_hearthstone_pids()

def cmd_status(args):
    """Show current Hearthstone status: PID, interface, server IP."""
    iface = get_active_interface() or "<none>"
    ips = get_all_logged_game_ips() or set()
    server = get_active_game_ip() or "<none>"
    if not pids:
        print("PID: <not running>")
    if pids:
        if len(pids) > 1:
            print(f"PID: {len(pids)} instances of Hearthstone found, close any extra instances or pfdc may not function.")
        else:
            print(f"PID: {pids[0]}")
    print(f"Interface: {iface}")
    if ips:
        print(f"IPs seen in log file: {', '.join(sorted(ips))}")
    else:
        print("IPs seen in log file: <none>")
    print(f"Active IP: {server}")

def cmd_paths(args):
    """Show relevant paths: Steam Library Paths, Hearthstone.exe Path, 
    Hearthstone Logs Path, Latest Log Directory Path, GameNetLogger.log Path"""
    steam_library_paths = get_steam_library_paths()
    hearthstone_path = get_hearthstone_install()
    hearthstone_logs_path = get_hearthstone_log_dir()
    latest_log_directory = get_latest_dir()
    gamenetlogger_path = find_game_net_logger()
    log_config_path = set_log_config()

    print(f"Steam Library Paths: {steam_library_paths or '<none>'}")
    print(f"Hearthstone Path: {hearthstone_path or '<none>'}")
    print(f"log.config Path: {log_config_path  or '<none>'}")
    print(f"Hearthstone Logs Path: {hearthstone_logs_path or '<none>'}")
    print(f"Latest Log Directory: {latest_log_directory or '<none>'}")
    print(f"GameNetLogger.log Path: {gamenetlogger_path  or '<none>'}")

def cmd_ips(args):
    """Dump all unique server IPs from the latest Hearthstone log."""
    ips = get_all_logged_game_ips()
    if ips:
        print("\n".join(sorted(ips)))
    else:
        print("No IPs found in logs.")

def cmd_active(args):
    """Print just the currently active server IP (if any)."""
    if pids:
        if len(pids) > 1:
            print(f"{len(pids)} instances of Hearthstone found, close any extra instances and try again.")
    active_ip = get_active_game_ip()
    if active_ip:
        print(active_ip)
    else:
        print("No active connection.")


def cmd_disconnect(args):
    """Drop one packet to force a quick reconnect."""
    if pids:
        if len(pids) > 1:
            print(f"{len(pids)} instances of Hearthstone found, close any extra instances and try again.")
            sys.exit(1)
    ok = start_disconnect(on_error=print)
    if ok:
        print("Disconnect triggered")
    else:
        print("Can't trigger disconnect")


def cmd_kill(args):
    """Terminate the Hearthstone process."""
    ok = kill_game(on_error=print)
    if ok:
        print("All instances of Hearthstone terminated.")
    sys.exit(0 if ok else 1)


def cmd_jeef(args):
    """Open Jeef comp tiers in browser."""
    webbrowser.open("https://hsreplay.net/battlegrounds/comps/")


def main():
    # RAINBOW = "\n".join([
    # "\033[41m" + " " * 44 + "\033[0m",  # red
    # "\033[43m" + " " * 44 + "\033[0m",  # yellow (as orange)
    # "\033[42m" + " " * 44 + "\033[0m",  # green
    # "\033[46m" + " " * 44 + "\033[0m",  # cyan (aqua)
    # "\033[44m" + " " * 44 + "\033[0m",  # blue
    # "\033[45m" + " " * 44 + "\033[0m",  # magenta (purple)
    # ])
    BOLD = '\033[1m'
    END = '\033[0m'
    parser = argparse.ArgumentParser(
        usage=argparse.SUPPRESS,
        description=BANNER + "\nProfunDC: Hearthstone network monitor & quick-disconnect tool.",
        prog='pfdc',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest='command', title=None, required=True, metavar=f'{BOLD}commands{END}')

    sub.add_parser(f"status", help=cmd_status.__doc__)
    sub.add_parser(f"paths", help=cmd_paths.__doc__)
    sub.add_parser(f"ips", help=cmd_ips.__doc__)
    sub.add_parser(f"active", help=cmd_active.__doc__)
    sub.add_parser("disconnect", help=cmd_disconnect.__doc__, aliases=["dc"])
    sub.add_parser(f"kill", help=cmd_kill.__doc__)
    sub.add_parser(f"jeef", help=cmd_jeef.__doc__)

    args = parser.parse_args()
    # dispatch
    {
        "status": cmd_status,
        "paths": cmd_paths,
        "ips": cmd_ips,
        "active": cmd_active,
        "disconnect": cmd_disconnect,
        "dc": cmd_disconnect,
        "kill": cmd_kill,
        "jeef": cmd_jeef,
    }[args.command](args)

if __name__ == "__main__":
    main()

