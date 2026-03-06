# Hamster Hunter Drone Menu

A drone-only mod menu for [Hamster Hunter](https://store.steampowered.com/app/2726490/Hamster_Hunter/) on Steam. Focused entirely on FPV drone controls, good for building and precision flying.

---

**drone-menu.exe** - Drone-focused menu:
- Adjust drone thrust, strafe, vertical speed, acceleration, and deceleration
- Bind keys or mouse side buttons to instantly set the drone's pitch and yaw
- Auto-clicker with hotkey toggle and configurable click delay

**Quality of life:**
- Waits for the game to launch on its own — no need to open in a specific order
- Automatically reconnects if the game is closed and reopened without restarting the menu
- Hover over any `?` icon for a description of what that value does
- Opacity slider to keep the menu visible without blocking your screen

---

## How to use

1. Open **drone-menu.exe** (run as Administrator — might be required for memory access)
2. Launch **Hamster Hunter** — the menu will attach automatically
3. The menu will show your current drone values once a drone is active

**Tips:**
- Press the tilde key (`~`) to toggle whether the menu stays on top of other windows
- For pitch/yaw hotkeys, click **Record**, press the key or mouse side button you want, enter the value, then click **Add**
- You can add multiple bindings per section and remove them individually
- The speed fields show the live in-game value when the drone is active
- If the game closes, the menu waits and reconnects when you relaunch — your bindings are preserved

---

## Windows Antivirus Warning

Windows Defender and other antivirus software may flag or automatically delete this program. This is a false positive.

The menu works by reading and writing memory in the game process, which is the same technique antiviruses use to detect cheats and malware. The program does nothing other than what is described above.

**If the exe gets deleted or blocked:**
- Check your antivirus quarantine and restore it
- Add an exclusion for the file or folder in Windows Defender settings
- Or run the Python source file directly instead (see below)

---

## Running from source

The full source code is included in this repository (`drone-menu.py`) so you can read exactly what the program does before running it.

To run from source you will need:

1. [Python 3.10 or newer](https://www.python.org/downloads/) — check "Add Python to PATH" during install
2. Open a terminal in the folder and run:

```
pip install customtkinter pymem pynput
```

3. Then run the script:

```
python drone-menu.py
```

Same as the exe, run as Administrator if memory access is denied.
