# 🎮 Peak & Aim Assistant

Professional gaming assistant for GameLoop emulator featuring automatic aim control while peaking and intelligent scope detection.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

- **Peak & Aim Control**: Automatically holds aim (O key) when peaking left (Q) or right (E)
- **Smart Scope Detection**: Disables aim when scoped (right-click detection)
- **In-Game Overlay**: Real-time status display with customizable position
- **Persistent Settings**: Saves all preferences automatically
- **System Tray Integration**: Runs minimized in background
- **Auto-Recovery**: Watchdog system prevents stuck keys
- **Multi-Emulator Support**: Works with GameLoop, BlueStacks, and other Android emulators

## 🎯 How It Works

1. **Press Q or E** → Automatically holds O (aim)
2. **Release Q or E** → Releases O
3. **Right-click (scope)** → Temporarily disables aim
4. **F8** → Toggle macro ON/OFF

## 📸 Screenshots

### Main Interface
![Main GUI](screenshots/main_gui.png)

### In-Game Overlay
![Overlay](screenshots/overlay.png)

## 🚀 Installation

### Method 1: Run from Source

1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation

2. **Clone the repository**
```bash
   git clone https://github.com/YOUR_USERNAME/peak-aim-assistant.git
   cd peak-aim-assistant
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Run the application**
```bash
   python peak_aim_assistant.py
```

### Method 2: Download Executable (Coming Soon)

Download the latest `.exe` from [Releases](https://github.com/YOUR_USERNAME/peak-aim-assistant/releases)

## 🎮 Usage

1. **Launch the application**
2. **Configure overlay position** (X, Y coordinates)
3. **Open GameLoop** and start your game
4. **Press F8** to activate the macro
5. **Use Q/E** to peak with automatic aim

See [detailed usage guide](docs/USAGE.md) for more information.

## ⚙️ Configuration

- **Overlay Position**: Set custom X, Y coordinates
- **Background**: Toggle semi-transparent background
- **Start Minimized**: Launch directly to system tray
- **Hotkeys**: F8 to toggle (customizable in future updates)

## 🔧 Requirements

- Windows 10/11
- Python 3.8 or higher (if running from source)
- GameLoop, BlueStacks, or compatible Android emulator

## 📝 Settings File

Settings are automatically saved in `settings.json`:
```json
{
  "overlay_x": 1600,
  "overlay_y": 50,
  "overlay_bg": true,
  "start_minimized": false
}
```

## 🛠️ Development

### Building from Source
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode
python peak_aim_assistant.py

# Build executable
pyinstaller --onefile --windowed --icon=icon.ico peak_aim_assistant.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📋 Roadmap

- [ ] Custom key bindings
- [ ] Multiple profiles
- [ ] Game-specific presets
- [ ] Statistics tracking
- [ ] Discord Rich Presence
- [ ] Auto-update feature

## ⚠️ Disclaimer

This tool is for educational and accessibility purposes only. Use at your own risk. The developers are not responsible for any consequences of using this software, including but not limited to game bans or penalties.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

Created with ❤️ by [Your Name]

## 🙏 Acknowledgments

- Built with Python and PyQt5
- Icons from [source if applicable]
- Inspired by the gaming community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/peak-aim-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/peak-aim-assistant/discussions)

---

⭐ Star this repository if you find it helpful!
