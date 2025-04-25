# ProfunDC (pfdc)

**Quick‑disconnect CLI for Hearthstone** (Linux)

A Python‑based command‑line tool that monitors Hearthstone’s GameNetLogger.log to identify game server IPs and simulate a network disconnection for a quick reconnect.

## 📦 Requirements

### System dependencies

Before running `./pfdc.sh`, ensure the following packages are installed on your system (your distro’s package manager may call them something slightly different):

- **dsniff** (provides the `tcpkill` command)
    
- **util-linux** (provides the `nsenter` command)
    
- **python3**
    

### Python dependencies

The install script (`pfdc.sh`) will automatically create a virtual environment and install all required Python packages, including:

- `psutil`
    
- `configobj`
    
- (plus any other dependencies defined in `pyproject.toml`)
    

## 📥 Installation

```bash
# Clone the repository
git clone https://github.com/fishspit/profundc.git
cd profundc

# One‑time setup & enter the ProfunDC shell:
./pfdc.sh

# Inside the new shell, try:
pfdc status
pfdc disconnect

# When done, exit back to your normal shell:
exit

# On subsequent runs, simply re‑launch:
./pfdc.sh
```

## 💻 Usage

```bash
# Show current game status
pfdc status

# List all logged server IPs
pfdc ips

# Display the currently active server IP
pfdc active

# Trigger a quick reconnect
pfdc disconnect

# Terminate all Hearthstone instances
pfdc kill

# Open Battlegrounds comp tiers in your browser
pfdc jeef
```

## 📝 Extra Notes

- **Disconnect behavior**: After running `pfdc disconnect`, you may need to interact with the game (e.g., hover over assets) to trigger network activity that the tool can catch and drop.
    
- If the game hangs or refuses to reconnect, it may be inactive (most likely match ended or you've been kicked). In that case, use `pfdc kill` and restart Hearthstone.
    
- This tool is unofficial; no statement from Blizzard indicates that using ProfunDC violates the Hearthstone ToS.

## 🐛 Reporting Issues

If you encounter any bugs or issues, please open an issue on the GitHub repository:

https://github.com/fishspit/profundc/issues

Include as much detail as possible: steps to reproduce, error messages, and your OS/distribution and version.

Alternatively, you can reach out to me via your GitHub (fishspit) 