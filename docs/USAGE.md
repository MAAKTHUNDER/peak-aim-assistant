# Usage Guide

## Quick Start

1. **Launch the Application**
   - Run `PeakAimAssistant.exe` or `python peak_aim_assistant.py`
   - The app will start in system tray (or show GUI on first run)

2. **Configure Settings**
   - Right-click tray icon → "Show GUI"
   - Set overlay position (default: X=1600, Y=50)
   - Enable/disable background
   - Configure startup behavior

3. **Start Gaming**
   - Open GameLoop and your game (PUBG Mobile, COD Mobile, etc.)
   - Press **F8** to activate the macro
   - The overlay will show status in-game

## Controls

### Hotkeys
- **F8**: Toggle macro ON/OFF
- **Q**: Peak left + Auto-aim
- **E**: Peak right + Auto-aim
- **Right-Click (tap)**: Toggle scope mode
- **Right-Click (hold)**: Temporary scope mode

### GUI Controls
- **Toggle Macro Button**: Same as F8
- **Apply & Save**: Save overlay position
- **Checkboxes**: Configure behavior

## Overlay

The overlay displays:
- **● ACTIVE** (Green): Macro is working
- **● INACTIVE** (Red): Macro is off
- **Scope: OPEN/CLOSED**: Current scope state

### Positioning Overlay

1. Open GameLoop in windowed mode
2. Note the top-right corner coordinates
3. Enter X, Y values in GUI
4. Click "Apply & Save"
5. Test in-game

**Example positions:**
- Top-right: X=1600, Y=50
- Top-left: X=50, Y=50
- Bottom-right: X=1600, Y=900

## Settings

### Show Background
- **ON**: Semi-transparent black background
- **OFF**: Text only (no background)

### Start Minimized
- **ON**: Starts in system tray
- **OFF**: Shows GUI window on startup

## System Tray

Right-click the tray icon for:
- **Show GUI**: Open main window
- **Toggle Macro**: Turn ON/OFF
- **Exit**: Close application

## Tips & Tricks

1. **Test First**: Try the macro in training mode before actual games
2. **Adjust Position**: Position overlay where it doesn't block important UI
3. **Scope Detection**: The app detects both tap and hold scope
4. **Performance**: Run in administrator mode for best performance
5. **Multiple Monitors**: Use screen coordinates for your gaming monitor

## Supported Emulators

- ✅ GameLoop (all versions)
- ✅ BlueStacks
- ✅ LDPlayer
- ✅ NoxPlayer
- ✅ MuMu Player

## Common Issues

### Macro not working
- Make sure F8 is pressed (overlay shows ACTIVE)
- Check if GameLoop window is in focus
- Run as administrator

### Overlay not visible
- Check if GameLoop is running
- Adjust X, Y coordinates
- Ensure overlay is within screen bounds

### Keys stuck
- Press F8 to disable macro
- Restart the application
- The watchdog should auto-recover

## Advanced Usage

### Custom Profiles (Coming Soon)
Create different profiles for different games:
- Profile 1: PUBG Mobile
- Profile 2: COD Mobile
- Profile 3: Free Fire

### Statistics (Coming Soon)
Track your usage:
- Total sessions
- Active time
- Peaks performed

## Safety

⚠️ **Important:**
- Use responsibly
- Check game's terms of service
- For accessibility and quality of life improvements
- Not for cheating or unfair advantage
