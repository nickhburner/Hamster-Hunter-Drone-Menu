# Hamster Hunter Mod Menu

A mod menu for [Hamster Hunter](https://store.steampowered.com/app/2726490/Hamster_Hunter/) on Steam. Lets you tweak drone (FPV) settings like speed and pitch/yaw hotkeys while you play.

---

**drone-menu.exe** - Full menu with everything:
- Adjust drone thrust, strafe, vertical speed, acceleration, and deceleration
- Bind keys or mouse side buttons to instantly set the drone's pitch and yaw

---

## How to use

1. Launch **Hamster Hunter** first
2. Open the menu exe (run as Administrator - might be required for memory access)
3. The menu will attach to the game automatically

**Tips:**
- Press the tilde key (`~`) to toggle whether the menu stays on top of other windows
- For pitch/yaw hotkeys, click **Record**, press the key or mouse side button you want, enter the value, then click **Add**
- You can add multiple bindings per section and remove them individually
- The drone speed fields show the current in-game value when the drone is active

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

1. [Python 3.10 or newer](https://www.python.org/downloads/) - check "Add Python to PATH" during install
2. Open a terminal in the folder and run:

```
pip install customtkinter pymem pynput
```

3. Then run the script:

```
python drone-menu.py
```

Same as the exe, the game must be running first and the script should be run as Administrator.
