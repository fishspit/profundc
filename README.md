# ProfunDC (pfdc)

**Quick-disconnect CLI for Hearthstone** (Linux)

This is a Python-based command-line tool that monitors Hearthstone's generated GameNetLogger.log to find game server IP's to use for simulating a network disconnection.


## Requirements
### **System** 
- Linux (Tested on Arch)
- Steam (Battle.net installed via "Add Non Steam Game" Proton/Wine)
- `dsniff` (To drop packets)
### **Python** :  
- Python 3.7+
- `psutil`
- `configobj`


## Installation
```bash
git clone https://github.com/fishspit/profundc.git
cd profundc

# One-time setup & enter CLI environment:
./pfdc.sh

# Inside the new shell:
pfdc status
pfdc disconnect
# …and more
exit

# Subsequent runs, from the same directory:
./pfdc.sh
```


## Usage
```bash
# show game status
pfdc status

# list all server IPs
pfdc ips

# show the currently active server
pfdc active

# quick reconnect
pfdc disconnect

# terminate Hearthstone
pfdc kill

# open Battlegrounds comp tiers
pfdc jeef
```


## Extra Notes:
- **Disconnection Notes**: For better functionality, after running `pfdc dc`, hover over random assets in-game to force a packet request. The disconnect logic works by watching packets to/from game-server, so leaving the game in an idle state may take longer than desired to trigger the disconnect.
- If you run `pfdc dc` and game refuses to reconnect and hangs on message, that most likely means the game is no longer active. (you either won, lost, or on very rare occasion been kicked from the lobby). Simply run `pfdc kill` and re-open Hearthstone.
- There has been no public word from Blizzard that I could find indicating or stating that a tool like this is against ToS.

